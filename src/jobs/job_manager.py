from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from arcgis.features import FeatureLayer, FeatureSet, Feature
from src.settings import settings
import json
from enum import Enum
import logging
import time
import asyncio
import importlib

from src.utils.date_utils import Agol_Now

LOGGER = logging.getLogger(__name__)


class JobStatus(Enum):
    CREATED = "CREATED"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobManager:
    """
    Class to manage jobs creation and execution. It is used
    by each of the standalone app instances running jobs and
    also by the main webapi to create new jobs.
    """

    agol: AgolAPI
    queue_ref: FeatureLayer

    def __init__(self):
        self.agol = AgolAPI_Injector()
        self.queue_ref = self.agol.get_table_ref(settings.agol_queue_feature_id)

    def add(self, name: str, params: dict):
        """
        Adds a job to the queue.

        Args:
            name: Name of the job. This has to be the qualified name of the class
                including the path for it to be included via reflection.
                If needed, extra data may be included after the class name by adding
                a ":" after it.
                E.g.: jobs.create_study_area.CreateStudyArea:123
            params: The parameters for the job. This dict will be saved into
                the queue as a JSON object and then read again for the job
                execution.
        """

        self.agol.add_list(
            self.queue_ref,
            [
                {
                    "attributes": {
                        "JOB_NAME": name,
                        "JOB_PARAMS": json.dumps(params),
                        "JOB_CREATE_DATE": Agol_Now(),
                        "JOB_STATUS": JobStatus.CREATED.value,
                    }
                }
            ],
        )

    def run_job(self, job: Feature):
        """
        Executes a job. The job is instantiated through reflection
        and then called asynchronously.

        Args:
            job: Job to be executed.
        """

        [full_class_name] = job.attributes["JOB_NAME"].split(":")
        LOGGER.info(f"Executing job <{full_class_name}>")

        module_name, class_name = full_class_name.rsplit(".", 1)
        module = importlib.import_module(f"src.{module_name}")
        class_ref = getattr(module, class_name)
        instance = class_ref()

        self.change_job_status(job, JobStatus.RUNNING)
        try:
            asyncio.run(instance.run(json.loads(job.attributes["JOB_PARAMS"])))
            self.change_job_status(job, JobStatus.COMPLETED)
        except Exception as e:
            LOGGER.error(f"Failed to execute job: {e}")
            self.change_job_status(job, JobStatus.FAILED)

    def change_job_status(self, job: Feature, status: JobStatus):
        """
        Updates the status of a job in the queue table.

        Args:
            job: Job to be executed.
            status: The new status.
        """

        job.attributes["JOB_STATUS"] = status.value
        if status == JobStatus.RUNNING:
            job.attributes["JOB_START_DATE"] = Agol_Now()
        elif status == JobStatus.COMPLETED:
            job.attributes["JOB_END_DATE"] = Agol_Now()
        self.agol.update(self.queue_ref, job)

    def _get_claimed_job(self):
        """
        Returns the job that is current claimed for the
        job executor.

        Returns:
            A job with status "CLAIMED" or "RUNNING" for the
            executing job executor.
        """

        job = self.queue_ref.query(
            where=f"""JOB_STATUS IN ('{JobStatus.CLAIMED.value}', '{JobStatus.RUNNING.value}') 
                 AND JOB_EXECUTOR_NAME = '{settings.job_manager_id}'""",
            order_by_fields="OBJECTID ASC",
        )
        if len(job.features):
            return job.features[0]
        return None

    def _claim_next_job(self):
        """
        Claims and returns the next available job for execution.
        If no job is available, returns None.

        Returns:
            The claimed job or None.
        """

        job_to_claim = self.queue_ref.query(
            where=f"JOB_STATUS = '{JobStatus.CREATED.value}'",
            order_by_fields="OBJECTID ASC",
            result_record_count=1,
            out_fields=["OBJECTID"],
        )

        if len(job_to_claim.features) == 1:
            self.queue_ref.calculate(
                where=f"""OBJECTID = {job_to_claim.features[0].attributes['OBJECTID']}
                    AND JOB_STATUS = '{JobStatus.CREATED.value}'
                    AND JOB_EXECUTOR_NAME IS NULL""",
                calc_expression=[
                    {"field": "JOB_STATUS", "value": f"'{JobStatus.CLAIMED.value}'"},
                    {
                        "field": "JOB_EXECUTOR_NAME",
                        "value": f"'{settings.job_manager_id}'",
                    },
                ],
            )

            return self._get_claimed_job()

    def _get_next_job(self):
        """
        Gets the next job for execution by this executor.
        If a job is already claimed, return it, otherwise return
        the next available job. If there are no jobs available, 
        return None.

        Returns:
            The next job this executor should execute.
        """

        job = self._get_claimed_job()
        if job is None:
            job = self._claim_next_job()
        return job

    def run(self):
        """
        Method to start a job executing routine. Should be used by
        standalone app instances exclusive for running jobs.
        This method will lock into a "while True" loop, looking for
        jobs and executing them.
        """

        LOGGER.info("Starting job manager")
        while True:
            time.sleep(settings.job_polling_time)
            LOGGER.info("Checking for jobs available for execution")
            job = self._get_next_job()
            if job is not None:
                self.run_job(job)
