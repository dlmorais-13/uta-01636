import os
import logging

from pathlib import Path
from arcgis.features import FeatureLayer, FeatureSet

from src.settings import settings
from src.apis.agol_api import AgolAPI
from src.utils.geopandas_utils import GeoPandasUtils
from src.models.config_repository import ConfigRepository

LOGGER = logging.getLogger(__name__)


class WaterRelatedLandUseUtils:
    """
    Class with utility function related to WRLU data.
    """

    @staticmethod
    def download_service_geojson(api: AgolAPI, service_id, county):
        """
        Download the data from a WRLU survey as GeoJson. Only the
        data from a given county is fetched. This method stores
        a cache of the downloaded data and uses it if necessary.

        Args:
            api: The ArcGIS API instance.
            service_id: The ID in ArcGIS for the WRLU layer.
            county: The county to filter the data.
        """

        geojson_path = os.path.join(
            settings.workdir,
            "geojson",
            f'{service_id}_{county.replace(" ", "-")}.geojson',
        )
        path = Path(geojson_path)

        if not path.exists():
            config_repository: ConfigRepository = ConfigRepository()

            ref: FeatureLayer = api.get_layer_ref(service_id)
            wrlu_land_use_columns = config_repository.get_config("WRLU_LAND_USE_COLUMNS").split(",")
            land_use_column = WaterRelatedLandUseUtils.get_land_use_column(
                ref, wrlu_land_use_columns
            )
            wrlu_land_use_values = config_repository.get_config("WRLU_LAND_USE_VALUES").split(",")
            land_use_values: str = ",".join(
                map(lambda v: f"'{v}'", wrlu_land_use_values)
            )

            wrlu_county_columns = config_repository.get_config("WRLU_COUNTY_COLUMNS").split(",")
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
        """
        Gets the name of the column in the FeatureLayer from WRLU that
        represents the land use by intersecting the possible land use
        columns with the columns existing in the layer.

        Args:
            feature_layer: The layer to look for the column.
            wrlu_land_use_columns: The list of possible columns with
                land use data.

        Returns:
            The column found.

        Raises:
            RuntimeError: if no column is found.
        """
        
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
        """
        Gets the name of the column in the FeatureLayer from WRLU that
        represents the county by intersecting the possible county
        columns with the columns existing in the layer.

        Args:
            feature_layer: The layer to look for the column.
            wrlu_county_columns: The list of possible columns with
                county data.

        Returns:
            The column found.

        Raises:
            RuntimeError: if no column is found.
        """
        
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
