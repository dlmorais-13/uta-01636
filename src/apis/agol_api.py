from colorama import Fore, Style
from camel_converter import to_snake
from arcgis.gis import GIS
from arcgis.features import (
    FeatureLayerCollection,
    FeatureLayer,
    Table,
    Feature,
    FeatureSet,
)
from typing import cast
from src.settings import settings
import logging

LOGGER = logging.getLogger(__name__)


class AgolAPI:

    gis: GIS
    config_cache: FeatureSet | None = None

    def __init__(self, token: str | None = None) -> None:
        LOGGER.info(f"Authenticating to {settings.agol_url} ... ")
        try:
            if token:
                self.gis = GIS(url=settings.agol_url, token=token)
            else:
                self.gis = GIS(
                    url=settings.agol_url,
                    client_id=settings.agol_client_id,
                    client_secret=settings.agol_client_secret,
                )
            LOGGER.info(f"{Fore.GREEN}✓ Authentication succeed.{Style.RESET_ALL}")
        except Exception as e:
            LOGGER.error(f"{Fore.RED}✕ Authentication failed: {e}{Style.RESET_ALL}")
            raise RuntimeError(
                f"Error authenticating to ArcGIS Online at URL {settings.agol_url}"
            ) from e

    def get_layer_ref(self, layer_id: str, layer_name: str = None) -> FeatureLayer:
        flc: FeatureLayerCollection = FeatureLayerCollection.fromitem(
            self.gis.content.get(layer_id)
        )
        if layer_name:
            return [l for l in flc.layers if l.properties.name == layer_name][0]
        return flc.layers[0] if flc else None

    def get_table_ref(self, table_id: str, table_name: str = None) -> Table:
        ref = self.gis.content.get(table_id)
        if table_name:
            return [t for t in ref.tables if t.properties.name == table_name][0]
        return ref.tables[0] if ref else None

    def query(
        self,
        layerIdOrRef: str | FeatureLayer,
        where: str,
        count: int = 1,
        order_by_fields="OBJECTID ASC",
    ):
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

    def update(self, layerIdOrRef: str | FeatureLayer, feature):
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

    def add_feature_collection(self, layerId: str, edits_payload: dict):
        LOGGER.info(f"Adding features to collection {layerId} ... ")
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

    def batch_edit(
        self,
        layerIdOrRef: str | FeatureLayer,
        features_to_add: list[Feature] = [],
        features_to_edit: list[Feature] = [],
        batch_size: int = 1000,
    ):
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
                self.edit_list(layerIdOrRef, to_add, to_edit)
        except Exception as e:
            raise RuntimeError("Error adding batch of features") from e

    def batch_add(
        self,
        layerIdOrRef: str | FeatureLayer,
        features: list[Feature],
        batch_size: int = 1000,
    ):
        LOGGER.info(f"Updating features on layer {layerIdOrRef}. Size {len(features)}")
        try:
            for i in range(0, len(features), batch_size):
                self.add_list(layerIdOrRef, features[i : i + batch_size])
        except Exception as e:
            raise RuntimeError("Error adding batch of features") from e

    def edit_list(
        self,
        layerIdOrRef: str | FeatureLayer,
        to_add: list[Feature],
        to_edit: list[Feature],
    ):
        try:
            ref = (
                layerIdOrRef
                if not isinstance(layerIdOrRef, str)
                else self.get_layer_ref(layerIdOrRef)
            )
            response = ref.edit_features(
                adds=cast(list[dict], to_add), updates=cast(list[dict], to_edit)
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
                f"{Fore.GREEN}{len(to_add)} records added. {len(to_edit)} records updated.{Style.RESET_ALL}"
            )
        except Exception as e:
            LOGGER.error(f"{Fore.RED}Error adding features: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error adding features") from e

    def add_list(self, layerIdOrRef: str | FeatureLayer, features: list[Feature]):
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
            LOGGER.info(f"{Fore.GREEN}{len(features)} records added.{Style.RESET_ALL}")
        except Exception as e:
            LOGGER.error(f"{Fore.RED}Error adding features: {e}{Style.RESET_ALL}")
            raise RuntimeError("Error adding features") from e

    def get_config(self, config_name: str) -> str:
        if self.config_cache is None:
            config_ref = self.get_table_ref(settings.agol_config_table_id)
            self.config_cache = config_ref.query()

        config = next(
            (
                c
                for c in self.config_cache.features
                if c.attributes["NAME"] == config_name
            ),
            None,
        )
        if config is None:
            raise RuntimeError(f"Config not found with name {config_name}")
        return config.attributes["CONFIG"]

    def get_configs(self, prefix: str = ""):
        if self.config_cache is None:
            config_ref = self.get_table_ref(settings.agol_config_table_id)
            self.config_cache = config_ref.query()

        return {
            c.attributes["NAME"]: c.attributes["CONFIG"]
            for c in self.config_cache.features
            if c.attributes["NAME"].startswith(prefix)
        }


class _AgolAPI_Injector:
    api: AgolAPI | None = None

    def __call__(self):
        if self.api is None:
            self.api = AgolAPI()
        return self.api


AgolAPI_Injector = _AgolAPI_Injector()
