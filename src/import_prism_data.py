from dotenv import load_dotenv
load_dotenv()  # noqa: E402 - Keep this instruction before the other import

import os
import shutil
import rasterio
from pyproj import Transformer
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import get_args, cast
from arcgis.features import Feature
from tqdm import tqdm

from agol_api import AgolAPI
from prism_downloader import PrismDownloader, PRISM_VARIABLES, PRISM_RESOLUTIONS, PRISM_INTERVALS

from logger import get_logger
LOGGER = get_logger(__name__)


def date_range_iterator(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += relativedelta(months=1)


def create_folder(path):
    folder_path = Path(path)
    folder_path.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    LOGGER.info('Executing Prism data import.')

    api = AgolAPI()

    # Retrieve the Prism centroid grid.
    centroid_layer_ref = api.get_layer_ref(os.environ['PRISM_800M_CENTROID_LAYER_ID'])
    LOGGER.info(f'Prism centroid layer ref: {centroid_layer_ref.url}')

    # Get the reference to the table to insert data.
    prism_data_table_ref = api.get_table_ref(os.environ['PRISM_800M_MONTHLY_TABLE_ID'])
    LOGGER.info(f'Prism 800m table ref: {prism_data_table_ref.url}')

    # Get the centroid layer coordinate system.
    prism_800m_sr = centroid_layer_ref.properties.extent.spatialReference
    point_wkid = prism_800m_sr.latestWkid if prism_800m_sr.latestWkid else prism_800m_sr.wkid
    LOGGER.info(f'AGOL Point CRS: EPSG:{point_wkid}')

    # Fetch the whole centroid layer data.
    LOGGER.info('Querying Prism centroids layer.')
    grid_fs = centroid_layer_ref.query(out_fields=["OBJECTID"], return_geometry=True)
    if grid_fs is None:
        raise Exception('Failed to get centroid layer reference.')
    centroid_points = [{"id": f.attributes["OBJECTID"], "x": f.geometry['x'], "y": f.geometry['y']}
                       for f in grid_fs.features]
    LOGGER.info(f'Prism centroid points: {len(centroid_points)}')
    LOGGER.info(f'Sample prism centroid point: {centroid_points[0]}')

    # Execution input variables
    workdir = os.path.abspath(os.path.join(os.getcwd(), os.environ['WORKDIR']))
    start_date = dt.fromisoformat(os.environ['START_DATE'])
    end_date = dt.fromisoformat(os.environ['END_DATE'])
    resolution = cast(PRISM_RESOLUTIONS, os.environ['RESOLUTION'])
    time_interval = cast(PRISM_INTERVALS, os.environ['TIME_INTERVAL'])
    variables = get_args(PRISM_VARIABLES)
    # variables = os.environ['VARIABLES'].split(',')

    # Control variables
    prism_downloader = PrismDownloader()
    expected_count = len(centroid_points)

    for date in date_range_iterator(start_date, end_date):
        date_folder_path = os.path.join(workdir, date.strftime('%Y%m'))
        create_folder(date_folder_path)
        LOGGER.info(f'Created folder: {date_folder_path}')

        where = f'NORMAL_MONTH = {date.month}'
        current_count = prism_data_table_ref.query(where, return_count_only=True)
        if current_count is None:
            raise Exception('Failed to get current count in Prism data table.')
        LOGGER.info(f'Found {current_count} records for {date.month}')

        if current_count == expected_count:
            LOGGER.info(f"Verified: {date.month} is complete. Skipping.")
            continue
        elif current_count > 0:
            LOGGER.info(
                f"Incomplete data ({current_count}/{expected_count}) for {date.month}. Repairing...")
            delete_result = prism_data_table_ref.delete_features(
                where=where, return_delete_results=False)
            if delete_result is None or (isinstance(delete_result, dict) and not delete_result['success']):
                raise Exception('Failed to delete incomplete data.')

        add_list: dict[str, Feature] = {}

        # Download and unzip the zip files for all variables
        for variable in variables:
            LOGGER.info(f'Downloading month/variable: {date.month}/{variable}')
            download_url = prism_downloader.get_download_url(
                resolution, cast(PRISM_VARIABLES, variable), time_interval, date)
            LOGGER.info(f'Loading Prism data from {download_url}')
            downloaded_file_path = prism_downloader.download(download_url, date_folder_path)
            unzipped_content_path = prism_downloader.unzip_file(downloaded_file_path)

            for filename in os.listdir(unzipped_content_path):
                if filename.endswith('.tif'):
                    try:
                        tif_path = os.path.join(unzipped_content_path, filename)
                        LOGGER.info(f'Processing GeoTIFF: {tif_path}')

                        with rasterio.open(tif_path) as dataset:
                            raster_crs = dataset.crs.to_string()
                            transformer = Transformer.from_crs(f"EPSG:{point_wkid}", raster_crs, always_xy=True)

                            transformed_coords = []
                            for p in centroid_points:
                                new_x, new_y = transformer.transform(p['x'], p['y'])
                                transformed_coords.append((new_x, new_y))

                            LOGGER.info(f'Sampling {tif_path}')
                            sample_gen = dataset.sample(transformed_coords)

                            for i, val in tqdm(enumerate(sample_gen)):
                                # val[0] is the pixel value; check for NoData
                                pixel_val = float(val[0])
                                if pixel_val == dataset.nodata:
                                    continue

                                cell_month_key = f'{centroid_points[i]['id']}/{date.month}'
                                if cell_month_key not in add_list:
                                    add_list[cell_month_key] = Feature(attributes={
                                        "CELL_ID": centroid_points[i]['id'],
                                        "NORMAL_MONTH": date.month
                                    })
                                add_list[cell_month_key].attributes[variable.upper()] = pixel_val
                    except Exception as e:
                        LOGGER.error(f'Failed to process {filename}: {e}')

        add_list_values = list(add_list.values())
        add_list_length = len(add_list_values)
        if add_list_length > 0:
            LOGGER.info(f'Adding list of features. Count: {add_list_length}. Sample: {add_list_values[0]}')
            api.batch_add(prism_data_table_ref, add_list_values)

        # Remove the unzipped folders, if they exist.
        if date_folder_path:
            unzipped_folder_list = [entry.name for entry in Path(date_folder_path).iterdir() if entry.is_dir()]
            for unzipped_folder in unzipped_folder_list:
                unzipped_folder_path = os.path.abspath(os.path.join(date_folder_path, unzipped_folder))
                if os.path.exists(unzipped_folder_path):
                    shutil.rmtree(unzipped_folder_path)
