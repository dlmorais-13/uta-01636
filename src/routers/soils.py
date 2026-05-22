from fastapi import APIRouter, Depends, Query
from typing import Annotated

from src.settings import settings
from src.apis.ssurgo_api import Ssurgo_API


router = APIRouter(
    prefix="/api/soils"
)

@router.get("/basic_data")
async def get_soils_basic_data(map_unit_ids: Annotated[list[str], Query()] = []):
    ssurgo_api = Ssurgo_API()
    map_unit_data = await ssurgo_api.get_map_unit_data(map_unit_ids)
    return map_unit_data
