import os
import json
import logging
from arcgis.features import FeatureSet
from geopandas import gpd

from src.jobs.job import Job
from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.prism_downloader import PrismDownloader
from src.utils.agol_geopandas_converter import AgolGeopandasConverter

LOGGER = logging.getLogger(__name__)


class CreatePrismMeshLayer(Job):
    """
    Class to create the prism mesh layers in AGOL.
    Will download the data from prism, intersect with the study area,
    and upload to AGOL.

    Usage:
    job = CreatePrismMeshLayer()
    await job.logic({
        'resolution': '800m'
    })

    Resolution must be either '800m' or '4km'.
    """

    async def logic(self, params: dict):
        resolution = params["resolution"]

        agol_api: AgolAPI = AgolAPI_Injector()

        study_area_layer_ref = agol_api.get_layer_ref(settings.agol_study_area_layer_id)
        study_area_feature_set: FeatureSet = study_area_layer_ref.query(
            where="1=1", return_geometry=True
        )

        # Instantiate a GeoDataFrame from the layer.
        study_area_gdf = gpd.GeoDataFrame.from_features(
            json.loads(study_area_feature_set.to_geojson),
            crs=f"EPSG:{settings.agol_default_crs}",
        )

        # Create a copy using the same coordinate system as of PRISM mesh.
        study_area_gdf_mesh_crs = study_area_gdf.to_crs(epsg=settings.prism_mesh_crs)
        LOGGER.info("Retrieved study area feature layer from AGOL.")

        prism_downloader = PrismDownloader()
        mesh_dir_path = prism_downloader.get_mesh_path(resolution)

        # List files in dir and get the name of file with extension .shp
        shp_file_name = [f for f in os.listdir(mesh_dir_path) if f.endswith(".shp")][0]

        mesh_features_gdf = gpd.read_file(
            os.path.join(mesh_dir_path, shp_file_name),
            bbox=tuple(study_area_gdf_mesh_crs.total_bounds),
        )

        # Project the GeoDataFrame to the same coordinate system as of study area layer.
        mesh_features_gdf.to_crs(epsg=settings.agol_default_crs, inplace=True)
        LOGGER.info(
            f"Loaded {len(mesh_features_gdf)} features from PRISM mesh with {resolution} resolution."
        )

        study_area_mesh_gdf = mesh_features_gdf.overlay(
            study_area_gdf, how="intersection"
        )
        study_area_mesh_gdf.drop(
            columns=[
                "STATE_NAME",
                "STATE_ABBR",
                "STATE_FIPS",
                "COUNTY_FIPS",
                "FIPS",
                "POPULATION",
                "POP_SQMI",
                "SQMI",
            ],
            inplace=True,
        )
        study_area_mesh_gdf.rename(columns={"NAME": "county"}, inplace=True)
        study_area_mesh_gdf.set_geometry("geometry", inplace=True)
        LOGGER.info(
            f"Intersected study area and PRISM mesh resulting in {len(study_area_mesh_gdf)} features."
        )

        mesh_layer_ref = agol_api.get_layer_ref(
            settings.agol_prism_mesh_layer_id, resolution
        )
        if params["delete"]:
            mesh_layer_ref.delete_features(where=f"1=1")

        # Add the features into AGOL layer.
        agol_api.batch_add(
            mesh_layer_ref,
            AgolGeopandasConverter.dataframeToFeatures(
                study_area_mesh_gdf, wkid=settings.agol_default_crs
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(CreatePrismMeshLayer().logic({"delete": True, "resolution": "800m"}))
