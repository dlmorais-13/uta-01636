from fastapi import APIRouter, Depends
from typing import Annotated

from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector


router = APIRouter(
    prefix="/api/parcels"
)

@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    return settings.agol_base_layer_view_id

@router.get("/config/study_area_counties")
async def get_parcels_study_area_counties(
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)]
):
    return api.get_config('STUDY_AREA_COUNTIES').split(',')
