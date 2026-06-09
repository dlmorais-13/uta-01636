from fastapi import APIRouter, Header, Depends
from typing import Annotated, Optional
from pydantic import BaseModel
from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.utils.admin_data_points import get_data_point, get_import_data, AdminData, ADMIN_DATA
from src.jobs.job_manager import JobManager
import logging

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin"
)


class Config(BaseModel):
    name: str
    config: str


@router.get("/configurations")
async def load_configurations(
    authorization: Annotated[str | None, Header()],
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)]
) -> list[Config]:
    configTable = api.get_table_ref(settings.agol_config_table_id)
    allConfigs = configTable.query()
    return [{
            'name': c.attributes['NAME'],
            'config': c.attributes['CONFIG']
            } for c in allConfigs.features]


@router.put("/configurations")
async def save_configurations(
    authorization: Annotated[str | None, Header()],
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)],
    desiredConfigs: list[Config] = None
):
    configTable = api.get_table_ref(settings.agol_config_table_id)

    allConfigs = configTable.query()

    deleteList = []
    editList = []
    addList = []
    existingConfigs = []

    for config in allConfigs.features:
        configName = config.attributes['NAME']
        existingConfigs.append(configName)

        # Returns the first dictionary where 'id' is 2
        desiredValue = next((dc['CONFIG'] for dc in desiredConfigs if dc["NAME"] == configName), None)

        if desiredValue is None:
            deleteList.append(config)
        else:
            config.attributes['CONFIG'] = desiredValue
            editList.append(config)

    newDesiredConfigs = [dc for dc in desiredConfigs if dc["NAME"] not in existingConfigs]
    for dc in newDesiredConfigs:
        addList.append({'attributes': dc})

    configTable.edit_features(
        adds=addList,
        updates=editList,
        deletes=deleteList
    )

    return True


@router.get("/data")
async def load_import_data(
    authorization: Annotated[str | None, Header()],
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)]
) -> list[AdminData]:
    return_values = []
    for data_point_id in ADMIN_DATA.keys():
        return_values.append(get_data_point(api, data_point_id))
    return return_values


@router.get("/data/{data_id}")
async def load_import_data_point(
    authorization: Annotated[str | None, Header()], 
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)],
    data_id: str
) -> AdminData:
    return get_data_point(api, data_id)


@router.get("/data/{data_id}/import/{import_id}")
async def process_import_data_point(
    authorization: Annotated[str | None, Header()],
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)],
    data_id: str,
    import_id: str
):
    return get_import_data(api, data_id, import_id)


@router.post("/data/{data_id}/import/{import_id}/process")
async def process_import_data_point(
    authorization: Annotated[str | None, Header()],
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)],
    data_id: str,
    import_id: str
):
    jobManager = JobManager(api)

    import_data = next((i for i in ADMIN_DATA[data_id].imports if i.id == import_id), None)
    if import_data is None:
        raise Exception('Failed to find data import configuration.')

    jobManager.add(import_data.job_name, {})
