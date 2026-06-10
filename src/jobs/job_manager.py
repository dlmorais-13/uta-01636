from src.apis.agol_api import AgolAPI
from arcgis.features import FeatureLayer, FeatureSet, Feature
from src.settings import settings
from datetime import datetime, timedelta
import pytz
import json
from enum import Enum
import logging
import time
import asyncio
import importlib

LOGGER = logging.getLogger(__name__)
TZ = pytz.timezone('America/Denver')


class JobStatus(Enum):
    CREATED = 'CREATED'
    CLAIMED = 'CLAIMED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class JobManager():

    agol: AgolAPI
    queue_ref: FeatureLayer

    def __init__(self, agol: AgolAPI):
        self.agol = agol
        self.queue_ref = self.agol.get_table_ref(settings.agol_queue_feature_id)

    def add(self, job_name: str, job_params: dict):
        self.agol.add_list(self.queue_ref, [
            {
                'attributes': {
                    'JOB_NAME': job_name,
                    'JOB_PARAMS': json.dumps(job_params),
                    'JOB_CREATE_DATE': TZ.localize(datetime.now()).isoformat(),
                    'JOB_STATUS': JobStatus.CREATED.value
                }
            }
        ])

    def get_status(self, job_name: str) -> JobStatus:
        jobs: FeatureSet = self.agol.query(
            self.queue_ref, f"JOB_NAME = '{job_name}'", order_by_fields="JOB_CREATE_DATE DESC")
        if not len(jobs.features):
            return None
        LOGGER.info(f'Job found: {jobs.features[0]}')
        return JobStatus[jobs.features[0].attributes['JOB_STATUS']]

    def run_job(self, job: Feature):
        [full_class_name] = job.attributes['JOB_NAME'].split(':')
        LOGGER.info(f'Executing job <{full_class_name}>')

        module_name, class_name = full_class_name.rsplit('.', 1)
        module = importlib.import_module(f'src.{module_name}')
        class_ref = getattr(module, class_name)
        instance = class_ref()

        self.change_job_status(job, JobStatus.RUNNING)
        try:
            asyncio.run(instance.run(json.loads(job.attributes['JOB_PARAMS'])))
            self.change_job_status(job, JobStatus.COMPLETED)
        except Exception as e:
            LOGGER.error(f'Failed to execute job: {e}')
            self.change_job_status(job, JobStatus.FAILED)

    def change_job_status(self, job: Feature, status: JobStatus):
        job.attributes['JOB_STATUS'] = status.value
        if status == JobStatus.RUNNING:
            job.attributes['JOB_START_DATE'] = TZ.localize(datetime.now()).isoformat()
        elif status == JobStatus.COMPLETED:
            job.attributes['JOB_END_DATE'] = TZ.localize(datetime.now()).isoformat()
        self.agol.update(self.queue_ref, job)

    def get_claimed_job(self):
        job = self.queue_ref.query(
            where=f"""JOB_STATUS IN ('{JobStatus.CLAIMED.value}', '{JobStatus.RUNNING.value}') 
                 AND JOB_EXECUTOR_NAME = '{settings.job_manager_id}'""",
            order_by_fields="OBJECTID ASC"
        )
        if len(job.features):
            return job.features[0]
        return None

    def claim_next_job(self):
        job_to_claim = self.queue_ref.query(
            where=f"JOB_STATUS = '{JobStatus.CREATED.value}'",
            order_by_fields="OBJECTID ASC",
            result_record_count=1,
            out_fields=["OBJECTID"]
        )

        if len(job_to_claim.features) == 1:
            self.queue_ref.calculate(
                where=f"""OBJECTID = {job_to_claim.features[0].attributes['OBJECTID']}
                    AND JOB_STATUS = '{JobStatus.CREATED.value}'
                    AND JOB_EXECUTOR_NAME IS NULL""",
                calc_expression=[
                    {"field": "JOB_STATUS", "value": f"'{JobStatus.CLAIMED.value}'"},
                    {"field": "JOB_EXECUTOR_NAME", "value": f"'{settings.job_manager_id}'"}
                ]
            )

            return self.get_claimed_job()

    def get_next_job(self):
        job = self.get_claimed_job()
        if job is None:
            job = self.claim_next_job()
        return job

    def run(self):
        LOGGER.info('Starting job manager')
        while (True):
            time.sleep(settings.job_polling_time)
            LOGGER.info('Checking for jobs available for execution')
            job = self.get_next_job()
            if job is not None:
                self.run_job(job)
