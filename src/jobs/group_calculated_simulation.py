import logging
import os
import geopandas as gpd
from pathlib import Path
from arcgis.geometry.filters import contains
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayer, Feature
from geopandas import GeoDataFrame

from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.utils.agol_geopandas_converter import AgolGeopandasConverter
from src.jobs.job import Job
from src.models.simulation_repository import SimulationRepository, SimulationColumns

LOGGER = logging.getLogger(__name__)


class GroupCalculatedSimulation(Job):
    """
    Job to group the values calculated in a simulation into the
    census tract areas.
    """

    api: AgolAPI
    simulation_repository: SimulationRepository
    simulation_layer_ref: FeatureLayer

    def __init__(self):
        super().__init__()
        self.api = AgolAPI_Injector()
        self.simulation_repository = SimulationRepository()
        self.simulation_layer_ref = self.api.get_layer_ref(
            settings.agol_simulations_layer_id
        )

    async def logic(self, params: dict):
        """
        Executes the job.

        Args:
            params: The job parameters as a dict with the following keys.
                - simulation_id: The ID of the simulation to process.
        """
        simulation_id = params["simulation_id"]

        LOGGER.info(f"Starting grouping of simulation {simulation_id}")
        tract_gdf = self.get_tract_gdf()
        tract_gdf["tid"] = tract_gdf.index
        LOGGER.info(f"Tract contains {len(tract_gdf)} features.")

        simulation = self.simulation_repository.get_simulation(simulation_id)
        start_year = simulation[SimulationColumns.START_YEAR.value]
        end_year = simulation[SimulationColumns.END_YEAR.value]
        for year in range(start_year, end_year + 1):
            LOGGER.info(f"Processing simulation {simulation_id} at year {year}.")

            year_feature_set = self.simulation_layer_ref.query(
                where=f"simulation_id = {simulation_id} and simulation_date = '{year}-01-01'",
                out_fields=["*"],
                return_all_records=True,
                return_geometry=True,
            )
            year_gdf = AgolGeopandasConverter.featuresToDataframe(year_feature_set)
            LOGGER.info(f"Year feature set contains {len(year_gdf)} features.")

            # Perform an overlay intersection to slice overlapping polygons.
            intersected = gpd.overlay(tract_gdf, year_gdf, how="intersection")

            # Set the area of each individual intersection piece.
            intersected["intersected_area"] = intersected.geometry.area

            # Compute the weighted value for each intersection.
            intersected["weighted_value"] = (
                intersected["carbon_stock"] * intersected["intersected_area"]
            )

            # Group by tract id, sum the values and area, then divide.
            aggregated = intersected.groupby("tid").agg(
                sum_weighted=("weighted_value", "sum"),
                sum_area=("intersected_area", "sum"),
            )
            aggregated["averaged_value"] = (
                aggregated["sum_weighted"] / aggregated["sum_area"]
            )

            # Merge the values back into the original tract gdf.
            merged_tract: GeoDataFrame = tract_gdf.merge(
                aggregated[["averaged_value"]],
                left_on="tid",
                right_index=True,
                how="inner",
            )
            print(merged_tract.head())

            tract_features = self.get_simulation_features_from_tracts(
                merged_tract, simulation_id, year
            )
            LOGGER.info(
                f"Tract based features calculated. Total {len(tract_features)} features."
            )

            self.api.batch_edit(
                self.simulation_layer_ref, features_to_add=tract_features
            )

    def get_simulation_features_from_tracts(
        self, tracts: GeoDataFrame, simulation_id: int, year: int
    ) -> list[Feature]:
        """ """

        tract_features = AgolGeopandasConverter.dataframeToFeatures(tracts.to_crs(4326))

        for t in tract_features:
            t.attributes["tract"] = t.attributes["FIPS"]
            t.attributes["simulation_date"] = f"{year}-01-01"
            t.attributes["carbon_stock"] = t.attributes["averaged_value"]
            t.attributes["simulation_id"] = simulation_id
            t.attributes["parcel_key"] = 0
            del t.attributes["OBJECTID"]
            del t.attributes["FIPS"]
            del t.attributes["POPULATION"]
            del t.attributes["tid"]
            del t.attributes["averaged_value"]

        return tract_features

    def get_tract_gdf(self):
        geojson_path = self.get_tract_geojson_path()

        if not Path(geojson_path).exists:
            study_area_extent = self.get_study_area_extent()
            spatial_filter = contains(geometry=Geometry(study_area_extent))

            tract_layer_ref = self.api.get_layer_ref(
                settings.usa_census_tracts_layer_id
            )
            tract_layer_feature_set = tract_layer_ref.query(
                geometry_filter=spatial_filter,
                out_fields=["FIPS", "POPULATION"],
                return_all_records=True,
                return_geometry=True,
            )
            tract_geojson = AgolGeopandasConverter.featureset_to_geojson(
                tract_layer_feature_set
            )
            with open(self.get_tract_geojson_path(), "w") as file:
                file.write(tract_geojson)
        tract_gdf: GeoDataFrame = gpd.read_file(geojson_path).to_crs(3857)
        return tract_gdf

    def get_study_area_extent(self):
        study_area_layer_ref = self.api.get_layer_ref(settings.agol_study_area_layer_id)
        return study_area_layer_ref.properties.extent

    def get_tract_geojson_path(self):
        return os.path.join(
            settings.workdir,
            "geojson",
            "tract.geojson",
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(GroupCalculatedSimulation().logic({"simulation_id": 5}))
