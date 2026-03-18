import os
from colorama import Fore, Style
from camel_converter import to_snake
from arcgis.gis import GIS, Folder, Group, Item, ItemProperties
from arcgis.features import FeatureLayerCollection, FeatureLayer, Table, Feature
from typing import cast, Literal

from logger import get_logger
LOGGER = get_logger(__name__)

AGOL_URL = os.environ.get('AGOL_URL')
AGOL_CLIENT_ID = os.environ.get('AGOL_CLIENT_ID')
AGOL_CLIENT_SECRET = os.environ.get('AGOL_CLIENT_SECRET')


class AgolAPI:

    gis: GIS
    group: Group

    def __init__(self) -> None:
        LOGGER.info(f'Authenticating to {AGOL_URL} ... ')
        try:
            self.gis = GIS(AGOL_URL, client_id=AGOL_CLIENT_ID, profile='default')
            self.group = self.gis.groups.get(os.environ['AGOL_PROJECT_GROUP_ID'])
            LOGGER.info(f'{Fore.GREEN}✓ Authentication succeed.{Style.RESET_ALL}')
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Authentication failed: {e}{Style.RESET_ALL}')
            raise RuntimeError(f'Error authenticating to ArcGIS Online at URL {AGOL_URL}') from e

    def item_exists(self, title: str, type: Literal['Feature Service']):
        search_result = self.group.search(query = f"title:'{title}' AND type:'{type}'")
        if search_result['total'] > 1:
            LOGGER.warning(f"More than 1 result returned in search for [title:'{title}' AND type:'{type}']: {search_result['total']}")
        return search_result['total'] > 0
    
    def get_layer_ref_from_name(self, name: str) -> FeatureLayer | None:
        type = 'Feature Service'
        search_result = self.group.search(query = f"title:'{name}' AND type:'{type}'")
        if search_result['total'] > 1:
            LOGGER.warning(f"More than 1 result returned in search for [title:'{name}' AND type:'{type}']: {search_result['total']}")
            return None
        return search_result['results'][0].layers[0]

    def get_layer_ref(self, layer_id: str) -> FeatureLayer:
        flc: FeatureLayerCollection = FeatureLayerCollection.fromitem(self.gis.content.get(layer_id))
        return flc.layers[0]

    def get_table_ref(self, table_id: str) -> Table:
        return self.gis.content.get(table_id).tables[0]

    def get_folder_ref(self, folder_id: str | None = None) -> Folder:
        return self.gis.content.folders.get(folder=folder_id if folder_id else os.environ['AGOL_PROJECT_FOLDER'])

    def query(self, layer_id: str, where: str, count: int = 1):
        LOGGER.info(f'Querying layer "{layer_id}" with condition "{where}" ... ')
        try:
            result = self.get_layer_ref(layer_id).query(
                where=where,
                return_all_records=False,
                result_record_count=count
            )
            LOGGER.info(f'{Fore.GREEN}✓ Query succeed.{Style.RESET_ALL}')
            return result
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Query error: {e}{Style.RESET_ALL}')
            raise RuntimeError('Error querying layer') from e

    def update(self, layer_id: str, feature):
        LOGGER.info(f'Updating feature {feature.attributes["OBJECTID"]} on layer "{layer_id}" ... ')
        try:
            result = self.get_layer_ref(layer_id).edit_features(updates=[feature])
            assert isinstance(result, dict)
            if result['updateResults'][0]['success']:
                LOGGER.info(f'{Fore.GREEN}✓ Update succeed{Style.RESET_ALL}')
                return result
            else:
                raise Exception(f'Unrecognizable response: {result}')
        except Exception as e:
            LOGGER.error(f'{Fore.RED}✕ Update error: {e}{Style.RESET_ALL}')
            raise RuntimeError('Error updating feature') from e

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

    def create_feature_layer(self, geojson: str, item_props: ItemProperties) -> Item:
        # Writing file to be uploaded
        workdir = os.path.abspath(os.path.join(os.getcwd(), os.environ['WORKDIR']))
        geojson_path = os.path.join(workdir, 'uploads', f'{to_snake(item_props.title)}.geojson')
        try:
            with open(geojson_path, 'w') as file:
                file.write(geojson)

            folder_ref: Folder = self.get_folder_ref()
            item_add_job = folder_ref.add(item_properties=item_props, file=geojson_path)
            geojson_item = item_add_job.result()
            geojson_item.sharing.groups.add(os.environ['AGOL_PROJECT_GROUP_ID'])
            LOGGER.info(f'Created GeoJson: {geojson_item}')

            layer_item: Item = geojson_item.publish()
            layer_item.sharing.groups.add(os.environ['AGOL_PROJECT_GROUP_ID'])

            return layer_item
        finally:
            if os.path.exists(geojson_path):
                os.unlink(geojson_path)
