"""
File to configure the routes related directly to parcels.
"""

from fastapi import APIRouter, Depends, Query
from typing import Annotated

from src.apis.ssurgo_api import Ssurgo_API
from src.settings import settings
from src.models.config_repository import ConfigRepository

router = APIRouter(prefix="/api/parcels")


@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    """
    Gets the ID in ArcGIS Online of the view with the public data
    of the parcels in the study area.
    """

    return settings.agol_base_layer_view_id


@router.get("/soils/basic_data")
async def get_soils_basic_data(map_unit_ids: Annotated[list[str], Query()] = []):
    """
    Gets the soil base data from SSURGO for the map unit ids indicated
    in the query parameters.

    Args:
        map_unit_ids: The list of IDs to fetch the data.

    Returns:
        The list of basic data for each map unit.
    """

    ssurgo_api = Ssurgo_API()
    map_unit_data = await ssurgo_api.get_map_unit_data(map_unit_ids)
    return map_unit_data
