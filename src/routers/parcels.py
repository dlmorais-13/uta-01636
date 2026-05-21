from fastapi import APIRouter, Depends
from typing import Annotated

from src.settings import settings
from src.agol_api import AgolAPI, AgolAPI_Injector


router = APIRouter(
    prefix="/api/parcels"
)

@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    return settings.agol_base_layer_view_id
