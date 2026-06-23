import logging
import os
import shutil
import zipfile
from pathlib import Path
import requests
from typing import Literal
from datetime import datetime as dt

from src.settings import settings

LOGGER = logging.getLogger(__name__)

PRISM_RESOLUTIONS = Literal['800m', '4km']
PRISM_VARIABLES = Literal['ppt', 'solclear', 'solslope', 'soltotal',
                          'soltrans', 'tdmean', 'tmax', 'tmean', 'tmin', 'vpdmax', 'vpdmin']
PRISM_WS_VARIABLES = Literal['ppt', 'tmin', 'tmax', 'tmean', 'tdmean', 'vpdmin', 'vpdmax']
PRISM_INTERVALS = Literal['monthly', 'daily']
PRISM_TYPES = Literal['normals', 'time_series']


class PrismDownloader():
    """
    Class for downloading PRISM climate data.
    """

    def get_mesh_path(self, resolution: PRISM_RESOLUTIONS) -> str:
        mesh_download_url = self._get_mesh_download_url(resolution)
        mesh_import_dir = os.path.join(settings.workdir, 'prism', 'mesh')
        mesh_downloaded_file_path = self._download(mesh_download_url, mesh_import_dir)
        return self._unzip_file(mesh_downloaded_file_path, overwrite=False)

    def get_data_path(self, resolution: PRISM_RESOLUTIONS, type: PRISM_TYPES, variable: PRISM_VARIABLES, interval: PRISM_INTERVALS, date: dt) -> str:
        data_download_url = self._get_download_url(resolution, type, variable, interval, date)
        date_in_name = date.strftime('%Y%m' if interval == 'monthly' else '%Y%m%d')
        data_import_dir = os.path.join(settings.workdir, 'prism', 'data', type, resolution, date_in_name)
        filename = None if type == 'normals' else f'{variable}.zip'
        data_downloaded_file_path = self._download(data_download_url, data_import_dir, filename=filename)
        return self._unzip_file(data_downloaded_file_path, overwrite=False) if data_downloaded_file_path is not None else None

    def _get_download_url(self, resolution: PRISM_RESOLUTIONS, type: PRISM_TYPES, variable: PRISM_VARIABLES, interval: PRISM_INTERVALS, date: dt) -> str:
        """
        Normals:
        - https://data.prism.oregonstate.edu/normals/us/800m/ppt/monthly/prism_ppt_us_30s_202001_avg_30y.zip
        Time Series:
        - https://services.nacse.org/prism/data/get/us/4km/tmin/202204?format=nc
        """
        resolution_in_name = '30s' if resolution == '800m' else '25m'
        date_in_name = date.strftime('%Y%m' if interval == 'monthly' else '%Y%m%d')

        if type == 'normals':
            return f'{settings.prism_base_url}/normals/us/{resolution}/{variable}/{interval}/prism_{variable}_us_{resolution_in_name}_{date_in_name}_avg_30y.zip'
        else:
            return f'{settings.prism_nacse_url}/us/{resolution}/{variable}/{date_in_name}?format=nc'

    def _get_mesh_download_url(self, resolution: PRISM_RESOLUTIONS) -> str:
        # https://prism.oregonstate.edu/downloads/data/prism_4km_mesh.zip
        return f'{settings.prism_mesh_base_url}/downloads/data/prism_{resolution}_mesh.zip'

    def _download(self, url: str, dest_folder: str, check_zip: bool = True, filename: str = None) -> str:
        filename = filename if filename is not None else url.split('/')[-1]
        os.makedirs(dest_folder, exist_ok=True)
        file_path = os.path.join(dest_folder, filename)

        # Ignore if file already exists but not if it is not a valid zip file.
        if not check_zip or not self._check_zip_integrity(file_path):
            try:
                LOGGER.info(f'Downloading file {url} ')

                # Make a GET request to the URL, set stream=True for large files
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                # Open the file in binary write mode ('wb') and write the content in chunks
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):  # Iterate over chunks
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)

                LOGGER.info(f'File successfully downloaded and saved to: {os.path.abspath(file_path)}')
            except requests.exceptions.HTTPError as httpError:
                if httpError.response.status_code == 404:
                    LOGGER.info(f'The PRISM URL "{url}" does not exist.')
                    return None
                else:
                    LOGGER.error(f'An error occurred: {httpError}')
            except requests.exceptions.RequestException as e:
                LOGGER.error(f'An error occurred: {e}')
        else:
            LOGGER.info(f'File {url} already downloaded')

        return file_path

    def _check_zip_integrity(self, path: str) -> bool:
        """Checks if path contains a valid zip file. If it does not and the path exists, the file in path is removed.

        Args:
            path: The path to be checked.

        Returns:
            bool indicating if there is a valid zip file at path.
        """

        try:
            if os.path.exists(path):
                zip_file = zipfile.ZipFile(path)
                zip_ok = zip_file.testzip()
                return zip_ok is None
        except:
            pass

        Path(path).unlink(True)
        return False

    def _unzip_file(self, file_path, overwrite: bool = True) -> str:
        zip_file = zipfile.ZipFile(file_path)
        dest_path = os.path.abspath(os.path.join(file_path, os.pardir, Path(file_path).stem))

        if os.path.exists(dest_path) and overwrite:
            shutil.rmtree(dest_path)
            zip_file.extractall(path=dest_path)
            return dest_path

        elif os.path.exists(dest_path) and not overwrite:
            return dest_path

        else:
            zip_file.extractall(path=dest_path)
            return dest_path
