from colorama import Fore, Style
from camel_converter import to_snake
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection, FeatureLayer, Table, Feature, FeatureSet
from typing import cast
from src.settings import settings
import logging

LOGGER = logging.getLogger(__name__)


class AgolAPI:

    gis: GIS
    config_cache: FeatureSet | None = None

    def __init__(self, token: str | None = None) -> None:
        LOGGER.info(f'Authenticating to {settings.agol_url} ... ')
        try:
            if token:
                self.gis = GIS(url=settings.agol_url, token=token)
            else:
                self.gis = GIS(url=settings.agol_url, client_id=settings.agol_client_id,
                               client_secret=settings.agol_client_secret)
            LOGGER.info(f'{Fore.GREEN}✓ Authentication succeed.{Style.RESET_ALL}')
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Authentication failed: {e}{Style.RESET_ALL}')
            raise RuntimeError(f'Error authenticating to ArcGIS Online at URL {settings.agol_url}') from e

    def get_layer_ref(self, layer_id: str) -> FeatureLayer:
        flc: FeatureLayerCollection = FeatureLayerCollection.fromitem(self.gis.content.get(layer_id))
        return flc.layers[0] if flc else None

    def get_table_ref(self, table_id: str) -> Table:
        ref = self.gis.content.get(table_id)
        return ref.tables[0] if ref else None

    def query(self, layerIdOrRef: str | FeatureLayer, where: str, count: int = 1, order_by_fields="OBJECTID ASC"):
        LOGGER.info(f'Querying layer "{layerIdOrRef}" with condition "{where}" ... ')
        try:
            ref = layerIdOrRef if not isinstance(layerIdOrRef, str) else self.get_layer_ref(layerIdOrRef)
            result = ref.query(
                where=where,
                return_all_records=False,
                result_record_count=count,
                order_by_fields=order_by_fields
            )
            LOGGER.info(f'{Fore.GREEN}✓ Query succeed.{Style.RESET_ALL}')
            return result
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Query error: {e}{Style.RESET_ALL}')
            raise RuntimeError('Error querying layer') from e

    def update(self, layerIdOrRef: str | FeatureLayer, feature):
        LOGGER.info(f'Updating feature {feature.attributes["OBJECTID"]} on layer "{layerIdOrRef}" ... ')
        try:
            ref = layerIdOrRef if not isinstance(layerIdOrRef, str) else self.get_layer_ref(layerIdOrRef)
            result = ref.edit_features(updates=[feature])
            assert isinstance(result, dict)
            if result['updateResults'][0]['success']:
                LOGGER.info(f'{Fore.GREEN}✓ Update succeed{Style.RESET_ALL}')
                return result
            else:
                raise Exception(f'Unrecognizable response: {result}')
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Update error: {e}{Style.RESET_ALL}')
            raise RuntimeError('Error updating feature') from e

    def add_feature_collection(self, layerId: str, edits_payload: dict):
        LOGGER.info(f'Adding features to collection {layerId} ... ')
        item = self.gis.content.get(layerId)
        flc = FeatureLayerCollection.fromitem(item)
        feature_service_url = flc.url

        response = self.gis._con.post(
            path=f"{feature_service_url}/applyEdits",
            postdata={
                "f": "json",
                "edits": edits_payload.__format__(''),
                "rollbackOnFailure": True,  # Ensures strict transactional behavior
                "useGlobalIds": False
            }
        )

        results_with_error = [ar for r in response for ar in r.get('addResults', []) if not ar['success']]
        if len(results_with_error):
            LOGGER.error(f'{Fore.RED}Add error: {results_with_error[0]} {Style.RESET_ALL}')
            raise Exception(f'Add error: {results_with_error[0]}')
        else:
            LOGGER.info(f'{Fore.GREEN}✓ Add succeed{Style.RESET_ALL}')

    def batch_add(self, layerIdOrRef: str | FeatureLayer, features: list[Feature], batch_size: int = 1000):
        LOGGER.info(f'Updating features on layer {layerIdOrRef}. Size {len(features)}')
        try:
            for i in range(0, len(features), batch_size):
                self.add_list(layerIdOrRef, features[i:i+batch_size])
        except Exception as e:
            raise RuntimeError('Error adding batch of features') from e

    def add_list(self, layerIdOrRef: str | FeatureLayer, features: list[Feature]):
        LOGGER.info(f'Updating features on layer {layerIdOrRef}. Size {len(features)}')
        try:
            ref = layerIdOrRef if not isinstance(layerIdOrRef, str) else self.get_layer_ref(layerIdOrRef)
            response = ref.edit_features(adds=cast(list[dict], features))
            if isinstance(response, dict) and 'addResults' in response:
                for result in response['addResults']:
                    if not result['success']:
                        LOGGER.error(f'{Fore.RED}Add error: {result["error"]["description"]}{Style.RESET_ALL}')
                        raise Exception(f'Add error: {result["error"]["description"]}')
            LOGGER.info(f'{Fore.GREEN}{len(features)} records added.{Style.RESET_ALL}')
        except Exception as e:
            LOGGER.error(f'{Fore.RED}Error adding features: {e}{Style.RESET_ALL}')
            raise RuntimeError('Error adding features') from e

    def get_config(self, config_name: str) -> str:
        if self.config_cache is None:
            config_ref = self.get_table_ref(settings.agol_config_table_id)
            self.config_cache = config_ref.query()

        config = next((c for c in self.config_cache.features if c.attributes['NAME'] == config_name), None)
        if config is None:
            raise RuntimeError(f'Config not found with name {config_name}')
        return config.attributes['CONFIG']

    def get_configs(self, prefix: str = ''):
        if self.config_cache is None:
            config_ref = self.get_table_ref(settings.agol_config_table_id)
            self.config_cache = config_ref.query()

        return {
            c.attributes['NAME']: c.attributes['CONFIG']
            for c in self.config_cache.features
            if c.attributes['NAME'].startswith(prefix)
        }
