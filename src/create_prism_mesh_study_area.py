"""
Script to import the PRISM mesh grid layer

Will download the mesh grid from PRISM website,
clip using the study area, and import into an AGOL feature layer.

Usage:
    python ./src/create_study_area_layer.py
"""

from dotenv import load_dotenv
load_dotenv()  # noqa: E402 - Keep this instruction before the other import

import os
import json
import geopandas as gpd
from arcgis.features import FeatureSet
from arcgis.gis import Folder, ItemProperties, ItemTypeEnum, Item
from typing import cast
from pathlib import Path

from agol_api import AgolAPI
from prism_downloader import PrismDownloader, PRISM_RESOLUTIONS

from logger import get_logger
LOGGER = get_logger(__name__)

AGOL_DEFAULT_CRS = os.environ['AGOL_DEFAULT_CRS']


def create_prism_layer_for_study_area():
    resolution = cast(PRISM_RESOLUTIONS, os.environ['RESOLUTION'])
    workdir = os.path.abspath(os.path.join(os.getcwd(), os.environ['WORKDIR']))
    mesh_import_dir = os.path.join(workdir, 'mesh_import')
    Path(mesh_import_dir).mkdir(parents=True, exist_ok=True)
    api = AgolAPI()

    mesh_study_area_layer_name = f'{os.environ["PROJECT_NAME"]} Study Area PRISM Mesh {resolution}'

    # Check if the layer already exists before doing anything.
    if api.item_exists(mesh_study_area_layer_name, 'Feature Service'):
        LOGGER.info(f'An item with type "Feature Service" and title "{mesh_study_area_layer_name}" already exists.')
        raise Exception(
            f'An item with type "Feature Service" and title "{mesh_study_area_layer_name}" already exists.')

    # Loads the study area feature layer from AGOL.
    study_area_layer_name = f'{os.environ["PROJECT_NAME"]} Study Area'
    study_area_layer_ref = api.get_layer_ref_from_name(study_area_layer_name)
    study_area_feature_set: FeatureSet = study_area_layer_ref.query(where="1=1", return_geometry=True)
    # Instantiate a GeoDataFrame from the layer.
    study_area_gdf = gpd.GeoDataFrame.from_features(
        json.loads(study_area_feature_set.to_geojson),
        crs=f'EPSG:{AGOL_DEFAULT_CRS}')
    # Create a copy using the same coordinate system as of PRISM mesh.
    study_area_gdf_mesh_crs = study_area_gdf.to_crs(epsg=os.environ['PRISM_MESH_CRS'])
    LOGGER.info('Retrieved study area feature layer from AGOL.')

    # Download the mesh information from PRISM.
    prism_downloader = PrismDownloader()
    mesh_download_url = prism_downloader.get_mesh_download_url(resolution)
    mesh_downloaded_file_path = prism_downloader.download(mesh_download_url, mesh_import_dir)
    mesh_unzipped_path = prism_downloader.unzip_file(mesh_downloaded_file_path, overwrite=False)
    shp_filename = f'prism_{resolution}_mesh.shp' if resolution == '4km' else f'prism{resolution}.shp'
    # Instantiate a GeoDataFrame from PRISM mesh, filtering the bounding box using the bounds of the study area.
    mesh_features_gdf = gpd.read_file(os.path.join(mesh_unzipped_path, shp_filename),
                                      bbox=tuple(study_area_gdf_mesh_crs.total_bounds))
    # Project the GeoDataFrame to the same coordinate system as of study area layer.
    mesh_features_gdf.to_crs(epsg=AGOL_DEFAULT_CRS, inplace=True)
    LOGGER.info(f'Loaded {len(mesh_features_gdf)} features from PRISM mesh with {resolution} resolution.')

    # Create a GeoDataFrame as the intersection of PRISM mesh and study area.
    study_area_mesh_gdf = mesh_features_gdf.overlay(study_area_gdf, how='intersection')
    study_area_mesh_gdf.drop(columns=[
        'STATE_NAME', 'STATE_ABBR', 'STATE_FIPS', 'COUNTY_FIPS', 'FIPS', 'POPULATION', 'POP_SQMI', 'SQMI'
    ], inplace=True)
    LOGGER.info(f'Intersected study area and PRISM mesh resulting in {len(study_area_mesh_gdf)} features.')

    return api.create_feature_layer(study_area_mesh_gdf.to_json(), ItemProperties(
        title=mesh_study_area_layer_name,
        item_type=ItemTypeEnum.GEOJSON
    ))


if __name__ == '__main__':
    LOGGER.info('Creating the PRISM grid layer for study area.')
    item = create_prism_layer_for_study_area()
    LOGGER.info(f"Successfully created and shared {item.title} (ID: {item.id})")
