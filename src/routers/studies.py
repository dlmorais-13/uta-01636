from fastapi import APIRouter, Depends
from typing import Annotated
import json

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings


router = APIRouter(
    prefix="/api/studies"
)

@router.get('/')
async def get_studies(
    api: Annotated[AgolAPI, Depends(AgolAPI_Injector)]
):
    study_table_ref = api.get_table_ref(settings.agol_studies_layer_id)
    feats = study_table_ref.query(
        where="1=1",
        return_all_records=True,
    )

    return [
        { **f.attributes, 'params': json.loads(f.attributes['params']) } 
        for f in feats.features
    ]
