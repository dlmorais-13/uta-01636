import os
import logging

from pathlib import Path
from arcgis.features import FeatureLayer, FeatureSet

from src.settings import settings
from src.apis.agol_api import AgolAPI
from src.utils.geopandas_utils import GeoPandasUtils

LOGGER = logging.getLogger(__name__)


class WaterRelatedLandUseUtils:

    @staticmethod
    def download_service_geojson(api: AgolAPI, service_id, county):
        geojson_path = os.path.join(
            settings.workdir,
            "geojson",
            f'{service_id}_{county.replace(" ", "-")}.geojson',
        )
        path = Path(geojson_path)

        if not path.exists():
            ref: FeatureLayer = api.get_layer_ref(service_id)
            wrlu_land_use_columns = api.get_config("WRLU_LAND_USE_COLUMNS").split(",")
            land_use_column = WaterRelatedLandUseUtils.get_land_use_column(
                ref, wrlu_land_use_columns
            )
            wrlu_land_use_values = api.get_config("WRLU_LAND_USE_VALUES").split(",")
            land_use_values: str = ",".join(
                map(lambda v: f"'{v}'", wrlu_land_use_values)
            )

            wrlu_county_columns = api.get_config("WRLU_COUNTY_COLUMNS").split(",")
            county_column = WaterRelatedLandUseUtils.get_county_column(
                ref, wrlu_county_columns
            )

            LOGGER.info(f"Downloading GeoJSON from {ref}")
            fs: FeatureSet = ref.query(
                where=f"""SHAPE IS NOT NULL 
                                                 AND {land_use_column} in ({land_use_values})
                                                 AND LOWER({county_column}) = '{county}'
                                                 """,
                return_all_records=True,
                return_geometry=True,
                out_sr=4326,
            )
            LOGGER.info(
                f"Downloaded FeatureSet. Type {type(fs)}, CRS: {fs.spatial_reference}"
            )

            geojson = GeoPandasUtils.featureset_to_geojson(fs)
            with open(geojson_path, "w") as file:
                file.write(geojson)
            return geojson
        else:
            LOGGER.info(f"GeoJSON already downloaded. Reading from cache.")
            return path.read_text()

    @staticmethod
    def get_land_use_column(
        featureLayer: FeatureLayer, wrlu_land_use_columns: list[str]
    ) -> str:
        columns = list(
            set([f["name"] for f in featureLayer.properties.fields])
            & set(wrlu_land_use_columns)
        )
        if len(columns) == 0:
            raise RuntimeError(
                f"Land use column not found. Available columns: {[f['name'] for f in featureLayer.properties.fields]}"
            )
        elif len(columns) > 1:
            LOGGER.warning(f"Multiple land use columns found: {columns}")
        return columns[0]

    @staticmethod
    def get_county_column(
        featureLayer: FeatureLayer, wrlu_county_columns: list[str]
    ) -> str:
        columns = list(
            set([f["name"] for f in featureLayer.properties.fields])
            & set(wrlu_county_columns)
        )
        if len(columns) == 0:
            raise RuntimeError(
                f"County column not found. Available columns: {[f['name'] for f in featureLayer.properties.fields]}"
            )
        elif len(columns) > 1:
            LOGGER.warning(f"Multiple county columns found: {columns}")
        return columns[0]
