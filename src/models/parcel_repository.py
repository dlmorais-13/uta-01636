from arcgis.features import FeatureLayer, Feature
import logging
import json

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings

LOGGER = logging.getLogger(__name__)


class ParcelRepository:
    """
    Repository class to control access to parcels data
    in the base layer for the study.
    """

    api: AgolAPI
    view_layer_ref: FeatureLayer
    base_layer_ref = FeatureLayer

    def __init__(self):
        self.api = AgolAPI_Injector()
        self.view_layer_ref = self.api.get_layer_ref(settings.agol_base_layer_view_id)
        self.base_layer_ref = self.api.get_layer_ref(settings.agol_base_layer_id)

    def get_parcels(self, where: str, return_geometry: bool = False) -> list[Feature]:
        """
        Retrieves a list of parcels from the base layer view using
        the given where clause as filter.

        Args:
          where: The filters to apply to the query.
          return_geometry: Whether the parcels geometries need to be returned.
        """

        LOGGER.info(f'Querying parcels with filters "{where}".')
        parcels = self.view_layer_ref.query(
            where=where, return_geometry=return_geometry, return_all_records=True
        )
        LOGGER.info(f"Found {len(parcels.features)} parcels.")
        return parcels.features

    def mark_map_unit_as_unusable(self, parcel: Feature, map_unit_id: int):
        """
        Marks a SSURGO map unit in a Parcel as unusable.

        Args:
            parcel: Partel to update.
            map_unit_id: The ID of the map unit to mark as unusable.
        """

        map_units = json.loads(parcel.attributes["map_unit_data"])
        map_unit = next((mu for mu in map_units if int(mu["id"]) == map_unit_id), None)
        map_unit["ignore"] = True
        parcel.attributes["map_unit_data"] = json.dumps(map_units)
        self.api.update(layerIdOrRef=self.base_layer_ref, feature=parcel)
        self.update_attachment_flags(parcel)

    def update_attachment_flags(self, parcel: Feature):
        """
        Update the attachment flags that indicate if all the necessary
        attachments for running simulations are available.

        Args:
            parcel: The parcel to check for the attachments.
        """

        attachments = self.api.get_attachments(
            layerIdOrRef=self.base_layer_ref, objectid=parcel.attributes["OBJECTID"]
        )

        types = ["equilibrium", "base"]
        map_unit_data: list[dict] = json.loads(parcel.attributes["map_unit_data"])
        target_count = len([mu for mu in map_unit_data if not mu.get("ignore", False)])

        for type in types:
            type_count = len([a for a in attachments if a["keywords"].startswith(type)])
            parcel.attributes[f"{type}_calculated"] = 1 if type_count == target_count else 0

        self.api.update(layerIdOrRef=self.base_layer_ref, feature=parcel)

    def upload_attachment(self, parcel: Feature, file_path: str, keywords: str):
        """
        Uploads an attachment to a parcel and marks the type of precalculation
        related to the attachment as complete, if necessary.

        Args:
            parcel: The parcel to update.
            file_path: The full path for the attachment.
            keywords: The keywords to add to the attachment.
        """

        self.api.add_attachment(
            layerIdOrRef=self.base_layer_ref,
            objectid=parcel.attributes["OBJECTID"],
            file_path=file_path,
            keywords=keywords,
        )
        self.update_attachment_flags(parcel)
