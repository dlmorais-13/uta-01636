"""
File to configure the routes related to studies.
"""

from fastapi import APIRouter
import logging

from src.settings import settings
from src.jobs.job_manager import JobManager
from src.models.study_repository import StudyRepository, StudyColumns

router = APIRouter(prefix="/api/studies")
LOGGER = logging.getLogger(__name__)


@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    """
    Gets the ID in ArcGIS Online of the public layer view
    with studies list and data.
    """

    return settings.agol_studies_layer_view_id


@router.get("/")
async def get_studies():
    """
    Gets the complete list of studies in the system.
    
    TODO: Might be necessary to page this or move entirely 
        to frontend using the public view.
    """

    return StudyRepository().list_studies()


@router.post("/")
async def create_study(body: dict):
    """
    Creates a new study in the system using the body data as
    configuration source.

    Args:
        body: The configuration for the study.

    Returns:
        The created study already with primary key set.
    """

    study = StudyRepository().create_study(body["filters"], body["parameters"])
    if study:
        jobManager = JobManager()
        jobManager.add(
            "jobs.process_created_study.ProcessCreatedStudy",
            dict(study_id=study[StudyColumns.OBJECTID.value]),
        )

    return study
