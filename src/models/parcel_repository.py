from arcgis.features import FeatureLayer, Feature
import logging

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings

LOGGER = logging.getLogger(__name__)


class ParcelRepository:
    """
    Repository class to control access to parcels data
    in the base layer for the study.
    """

    api: AgolAPI
    layer_ref: FeatureLayer

    def __init__(self):
        self.api = AgolAPI_Injector()
        self.layer_ref = self.api.get_layer_ref(settings.agol_base_layer_view_id)

    def get_parcels(self, where: str, return_geometry: bool = False) -> list[Feature]:
        """
        Retrieves a list of parcels from the base layer view using
        the given where clause as filter.

        Args:
          where: The filters to apply to the query.
          return_geometry: Whether the parcels geometries need to be returned.
        """

        LOGGER.info(f'Querying parcels with filters "{where}".')
        parcels = self.layer_ref.query(
            where=where, return_geometry=return_geometry, return_all_records=True
        )
        LOGGER.info(f"Found {len(parcels.features)} parcels.")
        return parcels.features
