from pydantic import BaseModel
from typing import Optional, Literal
from src.settings import settings
from src.agol_api import AgolAPI
from jobs.job_manager import JobManager, JobStatus
import logging

LOGGER = logging.getLogger(__name__)


class AdminDataImport(BaseModel):
    id: str
    name: str
    object_ref_id: str
    type: Literal['layer', 'table']
    expected_count: int
    count: Optional[int] = None
    lastEditDate: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None
    job_name: Optional[str] = None


class AdminData(BaseModel):
    id: str
    name: str
    description: str
    imports: list[AdminDataImport]


ADMIN_DATA: dict[str, AdminData] = {
    'study-area': AdminData(
        id='study-area',
        name='Study Area',
        description='Layer with the study area limits.',
        imports=[
            AdminDataImport(
                id='layer',
                name='Layer',
                job_name='jobs.create_study_area.CreateStudyArea',
                expected_count=11,
                type='layer',
                object_ref_id=settings.agol_study_area_layer_id
            )
        ]
    ),
    'base-layer': AdminData(
        id='base-layer',
        name='Base Layer',
        description='Layer with the parcels in the study area limits.',
        imports=[
            AdminDataImport(
                id='parcels',
                name='Parcels with historic data',
                job_name='jobs.create_base_layer.CreateBaseLayer',
                expected_count=0,
                type='layer',
                object_ref_id=settings.agol_base_layer_id
            )
        ]
    )
}


def get_data_point(agol: AgolAPI, data_id: str) -> AdminData:
    data_point: AdminData = ADMIN_DATA[data_id].model_copy()

    for i in data_point.imports:
        calculate_import_data(agol, i)

    return data_point


def calculate_import_data(agol: AgolAPI, import_data: AdminDataImport):

    if import_data.type == 'layer':
        agol_obj_ref = agol.get_layer_ref(import_data.object_ref_id)
    elif import_data.type == 'table':
        agol_obj_ref = agol.get_table_ref(import_data.object_ref_id)

    if agol_obj_ref:
        jobManager = JobManager(agol)
        import_data.count = agol_obj_ref.query(return_count_only=True)
        import_data.lastEditDate = agol_obj_ref.properties['editingInfo']['lastEditDate']
        import_data.url = f'{settings.agol_mapviewer_base_url}?layer={agol_obj_ref.properties["serviceItemId"]}'

        try:
            job_status = jobManager.get_status(import_data.job_name)
            match job_status:
                case JobStatus.CREATED | JobStatus.CLAIMED:
                    import_data.status = 'scheduled'
                case JobStatus.RUNNING:
                    import_data.status = 'in-progress'
        except Exception as e:
            LOGGER.debug(f'Job status exception: {e}')

        if not import_data.status:
            if import_data.expected_count > 0 and import_data.count == import_data.expected_count:
                import_data.status = 'fully-imported'
            elif import_data.expected_count > 0 and import_data.count > 0:
                import_data.status = 'partially-imported'
            elif import_data.expected_count > 0 and import_data.count == 0:
                import_data.status = 'not-imported'
            elif import_data.count == 0:
                import_data.status = 'not-imported'
            else:
                import_data.status = 'fully-imported'

    else:
        import_data.count = 0
        import_data.status = 'not-imported'


def get_import_data(agol: AgolAPI, data_id: str, import_data_id: str) -> AdminDataImport:
    data_point: AdminData = ADMIN_DATA[data_id]
    import_data = next((i for i in data_point.imports if i.id == import_data_id), None)
    import_data = import_data.model_copy()
    calculate_import_data(agol, import_data)
    return import_data
