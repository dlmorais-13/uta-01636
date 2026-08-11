from fastapi import APIRouter, Depends
from typing import Annotated
import json
from arcgis.features import Feature
import logging
from datetime import datetime as dt

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings

router = APIRouter(prefix="/api/studies")
LOGGER = logging.getLogger(__name__)


@router.get("/config/view_service_id")
async def get_parcels_view_service_id():
    return settings.agol_studies_layer_view_id


@router.get("/")
async def get_studies(api: Annotated[AgolAPI, Depends(AgolAPI_Injector)]):
    study_table_ref = api.get_table_ref(settings.agol_studies_layer_id)
    feats = study_table_ref.query(
        where="1=1",
        return_all_records=True,
    )

    return [
        {
            **f.attributes,
            "filters": json.loads(f.attributes["filters"]),
            "params": json.loads(f.attributes["params"]),
        }
        for f in feats.features
    ]


@router.post("/")
async def create_study(api: Annotated[AgolAPI, Depends(AgolAPI_Injector)], body: dict):
    LOGGER.info(body)
    table_ref = api.get_table_ref(settings.agol_studies_layer_id)

    # TODO How do define owner?
    result = api.add_list(
        table_ref,
        [
            Feature(
                attributes=dict(
                    filters=json.dumps(body["filters"]),
                    params=json.dumps(body["parameters"]),
                    owner="a02462576@usu.edu_usuonline",
                    status="created",
                    created_date=dt.now().isoformat(timespec="seconds"),
                )
            )
        ],
    )

    study_id = result[0]["objectId"]
    study = api.get_by_id(table_ref, study_id)
    return {
        **study.attributes,
        "filters": json.loads(study.attributes["filters"]),
        "params": json.loads(study.attributes["params"]),
    }
