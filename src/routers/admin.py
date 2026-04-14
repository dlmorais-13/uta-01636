from fastapi import APIRouter, Header
from typing import Annotated
from arcgis import GIS
from arcgis.features import Table
from src.settings import settings
import pandas as pd
import logging

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin"
)


@router.get("/configurations")
async def load_configurations(authorization: Annotated[str | None, Header()] = None):
    accessToken = authorization.split(' ')[1]
    gis: GIS = GIS(url=settings.agol_url, token=accessToken)

    configTable: Table = gis.content.get(settings.agol_config_table_id).tables[0]
    allConfigs = configTable.query()
    return {
        'envs': [
            { 'NAME': 'agol_url', 'CONFIG': settings.agol_url },
            { 'NAME': 'agol_client_id', 'CONFIG': settings.agol_client_id },
            { 'NAME': 'agol_client_secret', 'CONFIG': settings.agol_client_secret },
            { 'NAME': 'agol_config_table_id', 'CONFIG': settings.agol_config_table_id },
            { 'NAME': 'agol_default_crs', 'CONFIG': settings.agol_default_crs },
            { 'NAME': 'agol_project_folder', 'CONFIG': settings.agol_project_folder },
            { 'NAME': 'agol_project_group_id', 'CONFIG': settings.agol_project_group_id },
            { 'NAME': 'agol_project_name', 'CONFIG': settings.agol_project_name },
        ],
        'editable': [c.attributes for c in allConfigs.features]
    }


@router.put("/configurations")
async def save_configurations(authorization: Annotated[str | None, Header()] = None):
    accessToken = authorization.split(' ')[1]
    gis: GIS = GIS(url=settings.agol_url, token=accessToken)
    configTable: Table = gis.content.get(settings.agol_config_table_id).tables[0]

    allConfigs = configTable.query()

    desiredConfigs = [
        { 'NAME': 'STUDY_AREA_COUNTIES', 'CONFIG': 'Box Elder,Cache,Davis,Morgan,Rich,Salt Lake,Summit,Tooele,Utah,Wasatch,Weber' },
        { 'NAME': 'USA_CENSUS_COUNTIES_LAYER_ID', 'CONFIG': '14c5450526a8430298b2fa74da12c2f4' },
        { 'NAME': 'SSURGO_MAPUNITS_LAYER', 'CONFIG': '06e5fd61bdb6453fb16534c676e1c9b9' },
        { 'NAME': 'PRISM_BASE_URL', 'CONFIG': 'https://data.prism.oregonstate.edu/normals/us' },
        { 'NAME': 'PRISM_MESH_BASE_URL', 'CONFIG': 'https://prism.oregonstate.edu/downloads/data/prism_' },
        { 'NAME': 'PRISM_MESH_CRS', 'CONFIG': '4269' },
        { 'NAME': 'PRISM_DEFAULT_RESOLUTION', 'CONFIG': '4km' },
        { 'NAME': 'PRISM_DEFAULT_PERIODICITY', 'CONFIG': 'Monthly Normals' },
        { 'NAME': 'WRLU_REST_BASE_URL', 'CONFIG': 'https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services' },
        { 'NAME': 'WRLU_COUNTY_COLUMNS', 'CONFIG': 'COUNTY,County' },
        { 'NAME': 'WRLU_LAND_USE_COLUMNS', 'CONFIG': 'LANDUSE,Landuse' },
        { 'NAME': 'WRLU_LAND_USE_VALUES', 'CONFIG': 'IR,SubIR,Agricultural' },
        { 'NAME': 'WRLU_SPEC_2024', 'CONFIG': '59f814a1b3f34559b8bafdd98ec96cb6|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2023', 'CONFIG': '4a039b79054241128ff1932dc621d06a|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:|IRR_Eff:|IRR_Loss:' },
        { 'NAME': 'WRLU_SPEC_2022', 'CONFIG': 'c01eae79b3c2429295d9d924f42dc6da|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2021', 'CONFIG': '3602f55dbd6b498cbfcbc9cb22aa00db|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2020', 'CONFIG': '34148f3731b34e0eabda003c90ca7af7|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2019', 'CONFIG': '4658a3a0bafa41f78628c82d7cd36019|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2018', 'CONFIG': '4f1671cc9da441b3825ead1512a08e7b|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:|OBJECTID_1:|LUID:' },
        { 'NAME': 'WRLU_SPEC_2017', 'CONFIG': '9332d9e711ad4a638a9e1112888dd796|OBJECTID:OBJECTID|Landuse:|CropGroup:CropGroup|Description:Use|IRR_Method:Irrigation|Acres:|State:|County:County|Basin:Basin|SubArea:SubArea|Label_Class:|LABEL:UseLabel|Class_Name:UseClass|OldLanduse:|LU_Group:IrrigationGroup|SURV_YEAR:SurveyYear|Shape__Area:|Shape__Length:|OBJECTID_1:|LUID:' },
        { 'NAME': 'WRLU_SPEC_2015', 'CONFIG': 'e7d83700be34443bb4e007b5209c17fc|OBJECTID_12:OBJECTID|OBJECTID_1:|OBJECTID:|LABEL:UseLabel|LANDCOV:LandCov|DESCRIPTIO:Use|IRR_TYPE:Irrigation|LANDUSE:|ACRES:|BASIN:|COUNTYNBR:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|Shape_Leng:|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2010', 'CONFIG': '4aa71f4e1f1d4b5fa6494aa4c46f8ccc|OBJECTID_1:OBJECTID|OBJECTID:|LABEL:UseLabel|IRR_TYPE:Irrigation|DESCRIPTIO:Use|LANDUSE:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|OldLabel:|OldDescrip:|LANDCOV:LandCov|ACRES:|LUID:|BASIN:|COUNTYNBR:|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2007', 'CONFIG': 'ced25a1ced28418a86797b9deec8fc4f|OBJECTID:OBJECTID|BASIN:|COUNTYNBR:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|LANDCOV:LandCov|IRR_TYPE:Irrigation|DESCRIPTIO:Use|LABEL:UseLabel|LANDUSE:|OldLabel:|OldDescrip:|LUID:|ACRES:|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_2005', 'CONFIG': '995271fba62043e89be1ee86226fdd8c|OBJECTID:OBJECTID|BASIN:|COUNTYNBR:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|LANDCOV:LandCov|IRR_TYPE:Irrigation|DESCRIPTIO:Use|LABEL:UseLabel|LANDUSE:|OldLabel:|OldDescrip:|LUID:|ACRES:|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WLRU_SPEC_1999', 'CONFIG': 'b4a4af19ede0437db9f783efde3c546e|OBJECTID:OBJECTID|BASIN:|COUNTYNBR:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|LANDCOV:LandCov|DESCRIPTIO:Use|LANDUSE:Irrigation|OldDescrip:|LUID:|ACRES:|Shape__Area:|Shape__Length:' },
        { 'NAME': 'WRLU_SPEC_1992', 'CONFIG': '1813fd566c664a9294441be5c5649aa9|OBJECTID:OBJECTID|BASIN:|COUNTYNBR:|COUNTY:County|BASIN_NAME:Basin|SURV_YEAR:SurveyYear|LANDCOV:LandCov|DESCRIPTIO:Use|LANDUSE:Irrigation|OldDescrip:|LUID:|ACRES:|Shape__Area:|Shape__Length:' },
    ]

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
        addList.append({ 'attributes': dc })

    configTable.edit_features(
        adds=addList,
        updates=editList,
        deletes=deleteList
    )

    return True
