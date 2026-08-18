"""
File to configure the administration routes.

All routes are prefixed by "/api/admin" and they require
a valid authorization header.
"""

from fastapi import APIRouter, Header, Depends
from typing import Annotated
from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.models.config_repository import ConfigRepository, Config
import logging

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin")


@router.get("/configurations")
async def load_configurations(
    authorization: Annotated[str | None, Header()],
) -> list[Config]:
    """
    Gets the list of all configurations in the system.

    Args:
        authorization: The authorization header.

    Returns:
        The list of configurations.
    """

    return ConfigRepository().get_configs()


@router.put("/configurations")
async def save_configurations(
    authorization: Annotated[str | None, Header()],
    configs: list[Config] = None,
):
    """
    Updates the configurations to a desired state, read from request body.

    Args:
        authorization: The authorization header.
        configs: The desired list of configurations.
    """

    ConfigRepository().update_configs(configs)
    return True
