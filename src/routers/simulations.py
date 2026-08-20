"""
File to configure the routes related to simulations.
"""

from fastapi import APIRouter
import logging

from src.settings import settings
from src.jobs.job_manager import JobManager
from src.models.simulation_repository import SimulationRepository, SimulationColumns

router = APIRouter(prefix="/api/simulations")
LOGGER = logging.getLogger(__name__)


@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    """
    Gets the ID in ArcGIS Online of the public layer view
    with simulations list and data.
    """

    return settings.agol_simulations_layer_view_id


@router.get("/")
async def get_simulations():
    """
    Gets the complete list of simulations in the system.
    
    TODO: Might be necessary to page this or move entirely 
        to frontend using the public view.
    """

    return SimulationRepository().list_simulations()


@router.post("/")
async def create_simulation(body: dict):
    """
    Creates a new simulation in the system using the body data as
    configuration source.

    Args:
        body: The configuration for the simulation.

    Returns:
        The created simulation already with primary key set.
    """

    simulation = SimulationRepository().create_simulation(body["filters"], body["parameters"])
    if simulation:
        jobManager = JobManager()
        jobManager.add(
            "jobs.process_created_simulation.ProcessCreatedSimulation",
            dict(simulation_id=simulation[SimulationColumns.OBJECTID.value]),
        )

    return simulation
