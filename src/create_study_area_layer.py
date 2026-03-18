"""
Script to create the study area layer.

Will connect to AGOL to query the USA Census Counties layer, filter only the counties in the study area,
create a new layer with the filtered data, and upload the new layer to AGOL.

Usage:
    python ./src/create_study_area_layer.py
"""

from dotenv import load_dotenv
load_dotenv()  # noqa: E402 - Keep this instruction before the other import

import os
from arcgis.features import FeatureSet
from arcgis.gis import Folder, ItemProperties, ItemTypeEnum, Item

from agol_api import AgolAPI

from logger import get_logger
LOGGER = get_logger(__name__)


def create_study_area_layer():
    api = AgolAPI()

    study_area_layer_name = f'{os.environ["PROJECT_NAME"]} Study Area'

    # Check if study area already exists before doing anything.
    if api.item_exists(study_area_layer_name, 'Feature Service'):
        LOGGER.info(f'An item with type "Feature Service" and title "{study_area_layer_name}" already exists.')
        raise Exception(f'An item with type "Feature Service" and title "{study_area_layer_name}" already exists.')

    # Query the source layer filtering only the counties in the study area.
    usa_census_counties_layer_ref = api.get_layer_ref(os.environ['USA_CENSUS_COUNTIES_LAYER_ID'])
    counties = ', '.join(map(lambda c: f"'{c} County'", os.environ['STUDY_AREA_COUNTIES'].split(',')))
    filter = f"STATE_NAME = 'Utah' AND NAME IN ({counties})"
    study_area_featureset: FeatureSet = usa_census_counties_layer_ref.query(
        where=filter, return_all_records=True, return_geometry=True)
    LOGGER.info(f'Study area size: {len(study_area_featureset)} counties.')

    return api.create_feature_layer(study_area_featureset.to_geojson, item_props=ItemProperties(
        title=study_area_layer_name,
        item_type=ItemTypeEnum.GEOJSON
    ))


if __name__ == '__main__':
    LOGGER.info('Creating study area layer.')
    item = create_study_area_layer()
    LOGGER.info(f"Successfully created and shared {item.title} (ID: {item.id})")
