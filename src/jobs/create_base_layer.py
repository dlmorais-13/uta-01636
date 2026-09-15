import logging
import os
import gc
import re
import json
from pathlib import Path

from geopandas import GeoDataFrame
import geopandas as gpd
from arcgis.features import FeatureSet, FeatureLayer, Feature, Table
from arcgis.geometry import Polygon, filters
from shapely.ops import orient
from pandas import Series

from src.settings import settings
from src.jobs.job import Job
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.utils.geopandas_utils import GeoPandasUtils
from src.utils.water_related_land_use_utils import WaterRelatedLandUseUtils
from src.utils.agol_geopandas_converter import AgolGeopandasConverter
from src.models.config_repository import ConfigRepository

LOGGER = logging.getLogger(__name__)
GEOJSON_PATH = os.path.join(settings.workdir, "geojson")


class CreateBaseLayer(Job):
    """
    Job to populate the base layer parcels and land use history using
    data from SSURGO and Utah's Water-Related Land Use.
    """

    api: AgolAPI
    configRepository: ConfigRepository

    async def logic(self, params: dict):
        """
        Executes the job.

        Args:
            params: Dictionary with the keys below.
                - batch_size: Number of parcels uploaded concurrently.
                - delete_data: Whether data should be deleted before start.
                    Optional. Default to False.
                - delete_county_json: Whether county GeoJson cache should
                    be deleted before start. Optional. Default to False.
                - delete_soils_json: Whether soils GeoJson cache should be
                    deleted before start. Optiona. Default to False.
                - parcel_id: Parcel ID to be processed. If defined, all other
                    are going to be ignored. Useful for debugging purposes.
                    Optional. Default to None.
        """
        self.api = AgolAPI_Injector()
        self.configRepository = ConfigRepository()

        wrlu_specs = self.configRepository.get_configs("WRLU_SPEC_")
        lower_case_counties = [
            county.lower()
            for county in self.configRepository.get_config("STUDY_AREA_COUNTIES").split(",")
        ]

        base_layer_ref: FeatureLayer = self.api.get_layer_ref(
            settings.agol_base_layer_id
        )
        base_table_ref: Table = self.api.get_table_ref(settings.agol_base_layer_id)

        delete_data: bool = params["delete_data"] if "delete_data" in params else False
        if delete_data:
            base_layer_ref.delete_features(where="1=1")
            base_table_ref.delete_features(where="1=1")

        delete_county_json: bool = (
            params["delete_county_json"] if "delete_county_json" in params else False
        )
        if delete_county_json:
            [p.unlink() for p in Path(GEOJSON_PATH).glob("base_layer_*.geojson")]

        delete_soils_json: bool = (
            params["delete_soils_json"] if "delete_soils_json" in params else False
        )
        if delete_soils_json:
            [p.unlink() for p in Path(GEOJSON_PATH).glob("soils_*.geojson")]

        # Get the most recent year from the specs
        most_recent_year = [
            int(wrlu_year.split("_")[-1]) for wrlu_year in wrlu_specs.keys()
        ]
        most_recent_year.sort(reverse=True)
        most_recent_year = most_recent_year[0]
        LOGGER.info(f"Most recent survey year is {most_recent_year}")

        # For each county, process the data and uplods to ArcGIS Online.
        for county in lower_case_counties:
            LOGGER.info(f"Processing county {county}")

            self.build_county_geojson(county, most_recent_year, wrlu_specs)
            geojson_path = self.get_county_geojson_path(county)

            # Get the last feature added to the base_layer.
            last_feature = base_layer_ref.query(
                where=f"County = '{county}'",
                order_by_fields="parcel_key DESC",
                result_record_count=1,
                out_fields=["parcel_key"],
            )

            # If there are features added, delete the last one, to be sure it is
            # going to be fully processed next.
            if len(last_feature.features):
                last_feature_key = int(
                    last_feature.features[0].attributes["parcel_key"]
                )
                # Delete the last feature from layer and history to guarantee it is fully added.
                base_layer_ref.delete_features(where=f"parcel_key = {last_feature_key}")
                base_table_ref.delete_features(where=f"parcel_key = {last_feature_key}")
            else:
                last_feature_key = 0

            LOGGER.info(
                f"Last feature key: {last_feature_key}. Ignoring all parcels with key < {last_feature_key}."
            )

            # Iterate until the whole county data is processed, in batches.
            # This is important to save on memory usage, but also because
            # AGOL API does not respond well to large edit requests.
            counter = 0
            while True:
                county_base_gdf: GeoDataFrame = gpd.read_file(
                    geojson_path,
                    rows=slice(
                        counter * params["batch_size"],
                        (counter + 1) * params["batch_size"],
                    ),
                )
                if not len(county_base_gdf):
                    break

                # If processing only one feature, keep only it, else check the last added feature.
                if "parcel_id" in params:
                    county_base_gdf = county_base_gdf[
                        county_base_gdf["OBJECTID"].eq(params["parcel_id"])
                    ]
                else:
                    # Drop all the features with ID < last_feature_key
                    county_base_gdf = county_base_gdf[
                        county_base_gdf["OBJECTID"] >= last_feature_key
                    ]

                counter += 1
                if len(county_base_gdf):
                    county_base_gdf = county_base_gdf.to_crs(epsg=3857)
                    history = self.calculate_county_parcels_history(
                        county, county_base_gdf, wrlu_specs
                    )
                    self.save_data(
                        county_base_gdf,
                        history,
                        wrlu_specs,
                        county,
                        most_recent_year,
                        params["parcel_id"] if "parcel_id" in params else None,
                    )

    def build_county_geojson(self, county: str, most_recent_year: int, wrlu_specs):
        """
        Build the GeoJson file for a county, if it doesn't yet exists.

        Args:
            county: The lowercase name of the county.
            most_recent_year: The most recent year with surveys.
            wrlu_specs: The list of configuration for importing WRLU data.
        """

        if not self.county_geojson_exists(county):
            [wrlu_service_id, *columns] = wrlu_specs[
                f"WRLU_SPEC_{most_recent_year}"
            ].split(",")

            # Downloads the GeoJson file from WRLU data.
            geojson = WaterRelatedLandUseUtils.download_service_geojson(
                self.api, wrlu_service_id, county
            )
            LOGGER.info(f"Downloaded GeoJSON for WRLU {most_recent_year} - {county}.")

            wrlu_columns = {k: v for col in columns for k, v in [col.split(":", 1)]}
            wrlu_columns["OBJECTID"] = "OBJECTID"

            LOGGER.info(f"Reading columns {list(wrlu_columns.keys())} of GeoJSON.")
            county_base_gdf = gpd.read_file(geojson, columns=list(wrlu_columns.keys()))
            LOGGER.info(
                f"WRLU {most_recent_year} - {county} size: {len(county_base_gdf)}"
            )
            gc.collect()

            # Project to 3857
            county_base_gdf = county_base_gdf.to_crs(epsg=3857)

            LOGGER.info(f"GDF validity: {county_base_gdf.is_valid.all()}")
            if not county_base_gdf.is_valid.all():
                LOGGER.warning(
                    "Fixing invalid geometries in county_base_gdf using buffer(0)."
                )
                county_base_gdf["geometry"] = county_base_gdf.geometry.buffer(0)

            # Intersect with soils layer from SSURGO, and build the column with
            # the map unit data as a JSON object with the map unit key and area
            # intersected with each parcel.
            soils_gdf = self.get_soils_gdf(county)
            intersection_gdf = gpd.overlay(
                soils_gdf, county_base_gdf, how="intersection"
            )
            intersection_gdf["map_unit_data"] = (
                intersection_gdf.apply(
                    lambda row: {"id": row["mukey"], "area": row.geometry.area}, axis=1
                )
                if len(intersection_gdf)
                else {}
            )

            # The previous operation creates multiple rows for each parcel, if they
            # intersect more than one map unit. The next operations group the rows
            # using the column OBJECTID and combine the map unit data into a single
            # JSON object.
            intersection_grouped_gdf = (
                intersection_gdf.groupby("OBJECTID")["map_unit_data"]
                .apply(lambda x: json.dumps(list(x)))
                .reset_index()
            )
            county_base_gdf = county_base_gdf.merge(
                intersection_grouped_gdf, on="OBJECTID", how="left"
            )

            # Sort the dataframe by OBJECTID
            county_base_gdf = county_base_gdf.sort_values(by=["OBJECTID"])

            self.save_county_gdf(county, county_base_gdf)

    def calculate_county_parcels_history(
        self, county: str, county_base_gdf: GeoDataFrame, wrlu_specs
    ) -> list[Series]:
        """
        Builds a list of Pandas Series containing the full land use history
        from WRLU of the parcels in the given GeoDataFrame.

        Args:
            county: The lowercase name of the county being processed.
            county_base_gdf: The GeoDataFrame with the county's parcels.
            wrlu_specs: The list of WRLU import configurations.

        Returns:
            The list with the parcel's histories of land use.
        """

        history = []

        # Hold the area of the parcels to use to filter them later.
        parcel_areas = county_base_gdf.set_index("OBJECTID").geometry.area

        # For each year with survey, build the history for all parcels.
        for wrlu_year, wrlu_spec in wrlu_specs.items():
            [wrlu_service_id, *columns] = wrlu_spec.split(",")
            year = wrlu_year.split("_")[-1]

            # Download the WRLU GeoJson for the county and year.
            geojson = WaterRelatedLandUseUtils.download_service_geojson(
                self.api, wrlu_service_id, county
            )
            LOGGER.info(f"Retrieved GeoJSON for WRLU {year} - {county}.")

            wrlu_columns = {k: v for col in columns for k, v in [col.split(":", 1)]}
            wrlu_columns["OBJECTID"] = "OBJECTID"

            LOGGER.info(f"Reading columns {list(wrlu_columns.keys())} of GeoJSON.")
            year_gdf = gpd.read_file(geojson, columns=list(wrlu_columns.keys()))
            year_gdf = year_gdf.to_crs(epsg=3857)
            LOGGER.info(f"WRLU {year} - {county} size: {len(year_gdf)}")
            gc.collect()

            # Adds the year prefix to each column.
            rename_columns = {col: f"{year}_{col}" for col in list(wrlu_columns.keys())}
            year_gdf = year_gdf.rename(columns=rename_columns)
            gc.collect()

            LOGGER.info(f"GDF is valid: {year_gdf.is_valid.all()}")
            if not year_gdf.is_valid.all():
                LOGGER.warning(
                    f"Fixing invalid geometries in next_gdf for year {year} using buffer(0)."
                )
                year_gdf["geometry"] = year_gdf.geometry.buffer(0)

            LOGGER.info(f"Joining base layer with WRLU {year}")
            joined_gdf = gpd.sjoin(
                county_base_gdf, year_gdf, how="left", predicate="intersects"
            )

            LOGGER.info(f"Calculating the area of the intersections")
            joined_gdf["intersection_area"] = joined_gdf.apply(
                lambda row: (
                    row["geometry"]
                    .intersection(year_gdf.loc[int(row["index_right"]), "geometry"])
                    .area
                    if gpd.pd.notna(row["index_right"])
                    else 0
                ),
                axis=1,
            )

            land_use_code_column = [c for c in columns if ":land_use_code" in c][
                0
            ].split(":")[0]
            LOGGER.info(f"Column for land_use_code is {land_use_code_column}.")

            # Group all features with same OBJECTID and Land Use Code (according to column).
            # The area of the features must be summed. The remaining columns should have the first value.
            agg_rules = {
                col: "first" for col in joined_gdf.columns if col != "intersection_area"
            }
            agg_rules["intersection_area"] = "sum"
            joined_gdf = joined_gdf.groupby(
                ["OBJECTID", f"{year}_{land_use_code_column}"], as_index=False
            ).agg(agg_rules)

            # Filter only features with area > 1% of the total area for the corresponding parcel.
            # This is important to discard minor differences between the surveys.
            total_parcel_areas = joined_gdf["OBJECTID"].map(parcel_areas)
            joined_gdf = joined_gdf[
                joined_gdf["intersection_area"] > total_parcel_areas * 0.01
            ]

            LOGGER.info(
                f"Joined base layer with {year} resulting in {len(joined_gdf)} features."
            )
            for idx, row in joined_gdf.iterrows():
                history.append(row)
            gc.collect()

        return history

    def get_county_geojson_path(self, county: str) -> str:
        """
        Returns the path to the GeoJson file of a county.

        Args:
            county: The lowercase name of the county.

        Returns:
            The full path to the county's GeoJson file.
        """

        return os.path.join(
            settings.workdir,
            "geojson",
            f'base_layer_{county.replace(" ", "-")}.geojson',
        )

    def county_geojson_exists(self, county: str):
        """
        Checks if the GeoJson for a county exists in the
        working directory.

        Args:
            county: The lowercase name of the county.

        Returns:
            True if the file exists, False otherwise.
        """

        path = Path(self.get_county_geojson_path(county))
        return path.exists()

    def save_county_gdf(self, county: str, gdf: GeoDataFrame):
        """
        Saves a GeoDataFrame as a GeoJson into the
        county's GeoJson file.

        Args:
            county: The lowercase name of the county.
            gdf: The GeoDataFrame to save.
        """
        with open(self.get_county_geojson_path(county), "w") as file:
            file.write(gdf.to_json())

    def save_data(
        self,
        parcels: GeoDataFrame,
        history: list,
        wrlu_specs: dict,
        county: str,
        most_recent_year: int,
        parcel_id: int | None = None,
    ):
        """
        Save the computed data into ArcGIS Online.

        Args:
            parcels: The GeoDataFrame with the parcels to save.
            history: The list with the land use history of the parcels.
            wrlu_specs: The WRLU configurations.
            county: The lowercase name of the county being processed.
            most_recent_year: The year of the most recent survey.
            parcel_id: Used for debugging purposes only. If defined
                the data that would be saved will be printed instead.
                Optional. Defauls to None.
        """

        features_to_add = self.build_features_to_save(
            parcels, county, wrlu_specs, most_recent_year
        )
        history_to_add = self.build_history_to_save(history, wrlu_specs)

        if parcel_id is None:
            self.api.add_features_to_collection(
                settings.agol_base_layer_id, 0, features_to_add, 1, history_to_add
            )
        else:
            # If there is a parcel defined, just print for debugging.
            print(features_to_add)
            print(history_to_add)

    def build_features_to_save(
        self,
        parcels: GeoDataFrame,
        county: str,
        wrlu_specs: dict,
        most_recent_year: int,
    ) -> list[Feature]:
        """
        Transforms the given GeoDataFrame with the parcels data into a list of Features
        to be saved in ArcGIS Online.

        Args:
            parcels: The GeoDataFrame with the parcels data.
            county: The lowercase name of the county being processed.
            wrlu_specs: The WRLU configurations.
            most_recent_year: The year of the most recent survey.
        """

        [_, *most_recent_columns] = wrlu_specs[f"WRLU_SPEC_{most_recent_year}"].split(
            ","
        )

        basin_column_name = next(
            (
                col_spec.split(":")[0]
                for col_spec in most_recent_columns
                if col_spec.split(":")[1] == "basin"
            ),
            None,
        )

        basin_subarea_column_name = next((
            col_spec.split(":")[0]
            for col_spec in most_recent_columns
            if col_spec.split(":")[1] == "basin_subarea"
        ), None)

        layer_projected = parcels.to_crs(epsg=4326)

        # Get the name of the county with capitalized letters.
        county_name = [
            c_name
            for c_name in self.configRepository.get_config("STUDY_AREA_COUNTIES").split(",")
            if c_name.lower() == county
        ][0]

        features_to_add = []
        for _, row in layer_projected.iterrows():
            feature_attrs = row.drop("geometry").to_dict()

            new_feat_attr = {
                "parcel_key": int(feature_attrs["OBJECTID"]),
                "county": county_name,
                "basin": feature_attrs[basin_column_name],
                # TODO Reprocess with subarea being imported.
                "basin_subarea": feature_attrs[basin_subarea_column_name],
                "map_unit_data": feature_attrs["map_unit_data"],
                "equilibrium_calculated": 0,
                "base_calculated": 0
            }

            geom = Polygon(
                {
                    "hasZ": False,
                    "hasM": False,
                    "rings": AgolGeopandasConverter.geodataframeGeometryToArcgisRings(
                        row["geometry"]
                    ),
                    "spatialReference": {"wkid": 4326},
                }
            )

            features_to_add.append(Feature(attributes=new_feat_attr, geometry=geom))

        return features_to_add

    def build_history_to_save(
        self, history: list[Series], wrlu_specs: dict
    ) -> list[Feature]:
        """
        Convert the list of historical land use in Pandas Series format into
        a list of Features to be saved in ArcGIS Online.

        Args:
            history: The list to be converted.
            wrlu_specs: The WRLU configuration.

        Returns:
            The converted list.
        """

        history_to_add = []
        for h in history:
            # Get the year of the history item for the column names.
            # It's the number in the start of any column name that starts with a number.
            year = [
                int(h.split("_")[0])
                for h in h.axes[0].values
                if re.match(r"^\d\d\d\d", h)
            ][0]

            wrlu_spec = wrlu_specs[f"WRLU_SPEC_{year}"]
            [_, *columns] = wrlu_spec.split(",")

            survey_year = ""
            irr_type = ""
            land_use = ""
            land_use_code = ""
            crop = ""
            crop_group = ""

            # For each column from WRLU configuration, read its value
            # and define it in the appropriate variable, doing any
            # transformations as necessary.
            for c in columns:
                c_from, c_to = c.split(":")

                match c_to:
                    case "survey_year":
                        survey_year = h[f"{year}_{c_from}"]

                    case "irr_type":
                        irr_type = self.transform_irr_type(
                            h[f"{year}_{c_from}"] if h[f"{year}_{c_from}"] else ""
                        )

                    case "land_use":
                        if c_from == "DESCRIPTIO":
                            land_use = (
                                "Pasture"
                                if "pasture" in h[f"{year}_{c_from}"].lower()
                                else "Agricultural"
                            )
                        else:
                            land_use = (
                                h[f"{year}_{c_from}"] if h[f"{year}_{c_from}"] else ""
                            )

                    case "land_use_code":
                        land_use_code = (
                            h[f"{year}_{c_from}"] if h[f"{year}_{c_from}"] else ""
                        )

                    case "crop":
                        crop = h[f"{year}_{c_from}"] if h[f"{year}_{c_from}"] else ""

                    case "crop_group":
                        crop_group = (
                            h[f"{year}_{c_from}"] if h[f"{year}_{c_from}"] else ""
                        )

            history_to_add.append(
                {
                    "attributes": {
                        "parcel_key": int(h["OBJECTID"]),
                        "survey_year": survey_year,
                        "irr_type": irr_type,
                        "land_use": land_use,
                        "land_use_code": land_use_code,
                        "crop": crop,
                        "crop_group": crop_group,
                        "area": h["intersection_area"],
                    }
                }
            )

        # Deduplicate values with the exact same row data.
        history_to_add = [
            json.loads(s)
            for s in {json.dumps(d, sort_keys=True) for d in history_to_add}
        ]

        return history_to_add

    def transform_irr_type(self, irr_type: str):
        """
        Transform the irrigation type from WRLU into the 
        format normalized expected by the base layer.

        Args:
            irr_type: The WRLU irrigation type.
        """

        match irr_type:
            case "D" | "Drip":
                return "Drip"
            case "F" | "Flood":
                return "Flood"
            case "S" | "Sprinkler":
                return "Sprinkler"
            case "SubIR" | "Sub-irrigated":
                return "Sub-irrigated"
            case "IR":
                return "Irrigated"
            case _:
                return "Unknown"

    def get_soils_gdf(self, county: str) -> GeoDataFrame:
        """
        Gets the GeoDataFrame for the soils data of SSURGO for a 
        specific county. If there exists a GeoJson cached, will be used,
        otherwise it will be computed using ArcGIS public data and
        cached for future use.

        Args:
            county: The lowercase name of the county.
        """

        soils_geojson_path = os.path.join(
            settings.workdir, "geojson", f'soils_{county.replace(" ", "-")}.geojson'
        )
        path = Path(soils_geojson_path)

        if path.exists():
            return gpd.GeoDataFrame.from_features(
                json.load(open(soils_geojson_path))
            ).set_crs(3857)
        else:
            soils_ref = self.api.get_layer_ref(settings.ssurgo_mapunits_layer_id)
            study_area_ref = self.api.get_layer_ref(settings.agol_study_area_layer_id)

            county_feature = study_area_ref.query(
                where=f"LOWER(NAME) = '{county.lower()} county'",
                return_geometry=True,
                out_sr=3857,
            )
            county_bounding_box = county_feature.sdf.spatial.bbox

            spatial_filter = filters.intersects(
                geometry=county_bounding_box, sr={"wkid": 3857}
            )

            # Query the layer in ArcGIS filtering with the
            # bounding box of the county.
            fs: FeatureSet = soils_ref.query(
                where="SHAPE IS NOT NULL",
                return_all_records=True,
                return_geometry=True,
                geometry_filter=spatial_filter,
                out_fields=["mukey"],
                out_sr=3857,
            )

            geojson = GeoPandasUtils.featureset_to_geojson(fs)

            with open(soils_geojson_path, "w") as file:
                file.write(geojson)
            return gpd.GeoDataFrame.from_features(json.loads(geojson)).set_crs(3857)


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        CreateBaseLayer().logic(
            {
                "batch_size": 1000,
                "delete_data": False,
                "delete_county_json": False,
                "delete_soils_json": False,
                # 'parcel_id': 10239
            }
        )
    )
