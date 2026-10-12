from colorama import Fore, Style
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection, FeatureLayer, Table, Feature
from typing import cast
from src.settings import settings
import logging
import threading

LOGGER = logging.getLogger(__name__)
_SECRET_TOKEN = object()


class AgolAPI:
    """
    Class used to interact with ArcGIS Online (AGOL) api.
    Should be instantiated using only the injector AgolAPI_Injector.
    """

    gis: GIS
    """Reference to the api."""

    _latest_survey_year: int | None = None
    """Cache for the year of the last survey in the system."""

    def __init__(self, secret_token):
        if secret_token is not _SECRET_TOKEN:
            raise PermissionError("Constructor is private.")

        LOGGER.info(f"Authenticating to {settings.agol_url} ... ")
        try:
            self.gis = GIS(
                url=settings.agol_url,
                api_key=settings.agol_api_key,
            )
            LOGGER.info(f"GIS Context URL: {self.gis.url}")
            LOGGER.debug(f"GIS properties: {self.gis.properties}")
            LOGGER.info(f"{Fore.GREEN}✓ Authentication succeed.{Style.RESET_ALL}")
        except Exception as e:
            LOGGER.error(f"{Fore.RED}✕ Authentication failed: {e}{Style.RESET_ALL}")
            raise RuntimeError(
                f"Error authenticating to ArcGIS Online at URL {settings.agol_url}"
            ) from e

    def get_layer_ref(self, layer_id: str, layer_name: str = None) -> FeatureLayer:
        """
        Returns the reference to a layer in AGOL given its ID.
        If the name is provided, return the sublayer with the given name, else
        returns the first sublayer in the layer.

        Args:
            layer_id: ID of the layer in AGOL.
            layer_name: Name of the sublayer to retrieve, defaults to the first sublayer.

        Returns:
            The reference to the feature layer.
        """

        flc: FeatureLayerCollection = FeatureLayerCollection.fromitem(
            self.gis.content.get(layer_id)
        )
        if layer_name:
            return [l for l in flc.layers if l.properties.name == layer_name][0]
        return flc.layers[0] if flc else None

    def get_table_ref(self, table_id: str, table_name: str = None) -> Table:
        """
        Returns the reference to a subtable in layer in AGOL given the layer ID.
        If the name is provided, return the subtable with the given name, else
        returns the first subtable in the layer.

        Args:
            table_id: ID of the layer in AGOL.
            table_name: Name of the subtable to retrieve, defaults to the first subtable.

        Returns:
            The reference to the table.
        """

        ref = self.gis.content.get(table_id)
        if table_name:
            return [t for t in ref.tables if t.properties.name == table_name][0]
        return ref.tables[0] if ref else None

    def get_by_id(self, layerIdOrRef: str | FeatureLayer, id: int) -> Feature:
        """
        Retrieves a feature from AGOL in a layer by filters by its ID.

        Args:
            layerIdOrRef: The ID or reference to the layer/table to retrieve the feature.
            id: The ID of the object to retrieve.

        Returns:
            The retrieve feature.
        """
        return self.query(layerIdOrRef, f"OBJECTID = {id}").features[0]

    def query(
        self,
        layerIdOrRef: str | FeatureLayer,
        where: str,
        count: int = 1,
        order_by_fields="OBJECTID ASC",
    ) -> dict:
        """
        Runs a query over a layer/table and return the result.

        Args:
            layerIdOrRef: The ID or reference to the layer/table to run the query over it.
            where: The filters to apply to the query.
            count: The number of features to fetch.
                Optional, defaults to 1.
            order_by_fields: The order by instruction to be applied.
                Optional, defaults to "OBJECTID ASC".

        Returns:
            The query result.
        """

        LOGGER.info(f'Querying layer "{layerIdOrRef}" with condition "{where}" ... ')
        try:
            ref = (
                layerIdOrRef
                if not isinstance(layerIdOrRef, str)
                else self.get_layer_ref(layerIdOrRef)
            )
            result = ref.query(
                where=where,
                return_all_records=False,
                result_record_count=count,
                order_by_fields=order_by_fields,
            )
            LOGGER.info(f"{Fore.GREEN}✓ Query succeed.{Style.RESET_ALL}")
            return result
        except Exception as e:
            LOGGER.error(f"{Fore.RED}✕ Query error: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error querying layer") from e

    def update(self, layerIdOrRef: str | FeatureLayer, feature: Feature) -> dict:
        """
        Updates a single feature on a layer/table.
        If layerId is used, only layers can be updated. To update a feature in a table,
        the reference has to be passed as a argument.

        Args:
            layerIdOrRef: The ID of the layer or the ref to the FeatureLayer or Table.
            feature: Feature to be updated.

        Returns:
            The update result.
        """

        LOGGER.info(
            f'Updating feature {feature.attributes["OBJECTID"]} on layer "{layerIdOrRef}" ... '
        )
        try:
            ref = (
                layerIdOrRef
                if not isinstance(layerIdOrRef, str)
                else self.get_layer_ref(layerIdOrRef)
            )
            result = ref.edit_features(updates=[feature])
            assert isinstance(result, dict)
            if result["updateResults"][0]["success"]:
                LOGGER.info(f"{Fore.GREEN}✓ Update succeed{Style.RESET_ALL}")
                return result
            else:
                raise Exception(f"Unrecognizable response: {result}")
        except Exception as e:
            LOGGER.error(f"{Fore.RED}✕ Update error: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error updating feature") from e

    def add_features_to_collection(self, layerId: str, *args) -> dict:
        """
        Adds multiple lists of features into a feature layer collection.
        This method allows adding to different layers at the same time, within a transaction.

        Args:
            layerId: The ID of the feature layer collection.
            *args: Requires a even number of arguments. Each pair
                is the numeric id of the sublayer and the list of features to add
                to it.

        Returns:
            The transaction result.
        """

        LOGGER.info(f"Adding features to collection {layerId} ... ")

        if len(args) < 2 and len(args) % 2 != 0:
            raise RuntimeError(
                "Incorrect number of arguments to add feature to collection."
            )

        edits_payload: list[dict] = list()
        args_iterator = iter(args)
        for i1, i2 in zip(args_iterator, args_iterator):
            edits_payload.append({"id": i1, "adds": i2})

        item = self.gis.content.get(layerId)
        flc = FeatureLayerCollection.fromitem(item)
        feature_service_url = flc.url

        response = self.gis._con.post(
            path=f"{feature_service_url}/applyEdits",
            postdata={
                "f": "json",
                "edits": edits_payload.__format__(""),
                "rollbackOnFailure": True,  # Ensures strict transactional behavior
                "useGlobalIds": False,
            },
        )

        results_with_error = [
            ar for r in response for ar in r.get("addResults", []) if not ar["success"]
        ]
        if len(results_with_error):
            LOGGER.error(
                f"{Fore.RED}Add error: {results_with_error[0]} {Style.RESET_ALL}"
            )
            raise Exception(f"Add error: {results_with_error[0]}")
        else:
            LOGGER.info(f"{Fore.GREEN}✓ Add succeed{Style.RESET_ALL}")
        return response

    def batch_edit(
        self,
        layerIdOrRef: str | FeatureLayer,
        features_to_add: list[Feature] = [],
        features_to_edit: list[Feature] = [],
        batch_size: int = 1000,
    ):
        """
        Add/edit a list of features into a single feature layer, in batches.

        Args:
            layerIdOfRef: ID or reference to the layer.
            features_to_add: List of features to add to the layer.
                Optional. Default to an empty list.
            features_to_edit: List of features to edit in the layer.
                Optional. Default to an empty list.
            batch_size: Number of features being edited/added at the same time.
                This number is independent for each operation, for example, a value of 10
                mean that up to 10 features can be edited and up to another 10 can be added at
                the same time, to a maximum of 20.
                Optional. Default to 1000.
        """

        LOGGER.info(
            f"Updating features on layer {layerIdOrRef}. Size {len(features_to_add) + len(features_to_edit)}"
        )
        try:
            max_add_length = len(features_to_add)
            max_edit_length = len(features_to_edit)
            max_length = max(max_add_length, max_edit_length)

            for i in range(0, max_length, batch_size):
                to_add = (
                    features_to_add[i : i + batch_size] if i <= max_add_length else []
                )
                to_edit = (
                    features_to_edit[i : i + batch_size] if i <= max_edit_length else []
                )
                self._edit_list(layerIdOrRef, to_add, to_edit)
        except Exception as e:
            raise RuntimeError("Error adding/editing batch of features") from e

    def _edit_list(
        self,
        layerIdOrRef: str | FeatureLayer,
        features_to_add: list[Feature] = [],
        features_to_edit: list[Feature] = [],
    ):
        """
        Add/edit a list of features into a single feature layer in a single operation.

        Args:
            layerIdOrRef: ID or reference to the layer.
            features_to_add: List of features to add to the layer.
                Optional. Default to an empty list.
            features_to_edit: List of features to edit in the layer.
                Optional. Default to an empty list.
        """

        try:
            ref = (
                layerIdOrRef
                if not isinstance(layerIdOrRef, str)
                else self.get_layer_ref(layerIdOrRef)
            )
            response = ref.edit_features(
                adds=cast(list[dict], features_to_add),
                updates=cast(list[dict], features_to_edit),
            )
            if isinstance(response, dict) and "addResults" in response:
                for result in response["updateResults"]:
                    if not result["success"]:
                        LOGGER.error(
                            f'{Fore.RED}Add error: {result["error"]["description"]}{Style.RESET_ALL}'
                        )
                        raise Exception(f'Add error: {result["error"]["description"]}')

                for result in response["addResults"]:
                    if not result["success"]:
                        LOGGER.error(
                            f'{Fore.RED}Add error: {result["error"]["description"]}{Style.RESET_ALL}'
                        )
                        raise Exception(f'Add error: {result["error"]["description"]}')

            LOGGER.info(
                f"{Fore.GREEN}{len(features_to_add)} records added. {len(features_to_edit)} records updated.{Style.RESET_ALL}"
            )
            return response
        except Exception as e:
            LOGGER.error(f"{Fore.RED}Error adding features: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error adding features") from e

    def add_list(
        self, layerIdOrRef: str | FeatureLayer, features: list[Feature]
    ) -> list[dict]:
        """
        Add a list of features into a feature layer.

        Args:
            layerIdOrRef: ID or reference to the layer.
            features: List of features to add to the layer.

        Returns:
            The results of the add operations.
        """
        LOGGER.info(f"Updating features on layer {layerIdOrRef}. Size {len(features)}")
        try:
            ref = (
                layerIdOrRef
                if not isinstance(layerIdOrRef, str)
                else self.get_layer_ref(layerIdOrRef)
            )
            response = ref.edit_features(adds=cast(list[dict], features))
            if isinstance(response, dict) and "addResults" in response:
                for result in response["addResults"]:
                    if not result["success"]:
                        LOGGER.error(
                            f'{Fore.RED}Add error: {result["error"]["description"]}{Style.RESET_ALL}'
                        )
                        raise Exception(f'Add error: {result["error"]["description"]}')
                LOGGER.info(
                    f"{Fore.GREEN}{len(features)} records added.{Style.RESET_ALL}"
                )
                return response["addResults"]
            else:
                raise Exception(f"Add error: {response}")
        except Exception as e:
            LOGGER.error(f"{Fore.RED}Error adding features: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error adding features") from e

    def get_latest_survey_year(self) -> int:
        """
        Get the year of the lastest survey stored in Agol API.

        Returns:
            The year of the lastest survey.
        """

        if self._latest_survey_year is None:
            layer_ref = self.get_layer_ref(settings.agol_base_layer_view_id)
            result = layer_ref.query(
                out_statistics=[
                    {
                        "statisticType": "max",
                        "onStatisticField": "survey_year",
                        "outStatisticFieldName": "max_val",
                    }
                ]
            )
            self._latest_survey_year = result.features[0].attributes["max_val"]
        return self._latest_survey_year

    def add_attachment(
        self,
        layerIdOrRef: str | FeatureLayer,
        objectid: int,
        file_path: str,
        keywords: str | None = None,
    ):
        """
        Adds an attachment to a feature in a feature layer.

        Args:
            layerIdOrRef: ID or reference to the layer.
            objectid: ID of the feature to add the attachment.
            file_path: Full path of the file to attach.
        """

        ref = (
            layerIdOrRef
            if not isinstance(layerIdOrRef, str)
            else self.get_layer_ref(layerIdOrRef)
        )

        current_attachments = self.get_attachments(ref, objectid)
        same_attachment = [a for a in current_attachments if a["keywords"] == keywords]

        # If there are other attachments with the same keyword,  delete them before.
        # adding the new one.
        if len(same_attachment) > 0:
            for a in same_attachment:
                ref.attachments.delete(objectid, a["id"])

        add_result = ref.attachments.add(
            oid=objectid, file_path=file_path, keywords=keywords
        )
        LOGGER.info(f"Add attachment result: {add_result}")

    def get_attachments(self, layerIdOrRef: str | FeatureLayer, objectid: int) -> dict:
        """
        Get the list of attachments for a given feature in a layer.

        Args:
            layerIdOrRef: ID or reference to the layer.
            objectid: ID of the feature to add the attachment.

        Returns:
            The dict with the list of attachments.
        """

        ref = (
            layerIdOrRef
            if not isinstance(layerIdOrRef, str)
            else self.get_layer_ref(layerIdOrRef)
        )
        attachment_list = ref.attachments.get_list(oid=objectid)
        LOGGER.info(attachment_list)
        return attachment_list

    def download_attachment(
        self,
        layerIdOrRef: str | FeatureLayer,
        objectid: int,
        attachment_id: str,
        save_path: str,
    ):
        """
        Downloads a given attachment from a feature in a layer.

        Args:
            layerIdOrRef: ID or reference to the layer.
            objectid: ID of the feature to add the attachment.
            attachment_id: The ID of the attachment.
            save_path: Full path to save the attachment.
        """
        ref = (
            layerIdOrRef
            if not isinstance(layerIdOrRef, str)
            else self.get_layer_ref(layerIdOrRef)
        )
        ref.attachments.download(objectid, attachment_id, save_path)


class _AgolAPI_Injector:
    """
    Class to inject the AgolAPI instance into received http requests.
    Also used to get the AgolAPI singleton instance.

    Example:

        from src.apis.agol_api import AgolAPI, AgolAPI_Injector
        api: AgolAPI = AgolAPI_Injector()
    """

    api: AgolAPI | None = None
    _lock = threading.Lock()

    def __call__(self):
        if self.api is None:
            with self._lock:
                if self.api is None:
                    self.api = AgolAPI(_SECRET_TOKEN)
        return self.api


AgolAPI_Injector = _AgolAPI_Injector()
