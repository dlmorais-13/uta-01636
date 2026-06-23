import os
import tempfile
import shutil
import logging
import json

from src.settings import settings
from src.utils.build_soilsin import BuildSoilsin
from src.utils.build_weather_file import BuildWeatherFile
from src.apis.agol_api import AgolAPI, AgolAPI_Injector


LOGGER = logging.getLogger(__name__)

class DaycentExecutor:
    """
    Class to execute Daycent for a given parcel and study.

    Will create a temporary execution folder, copy all necessary static files,
    invoke the creation of the parameter files, execute the Daycent analysis,
    and upload the results into the ArcGIS online layer with study results data.

    Usage:
        executor = DaycentExecutor()
        await executor.execute(parcel_id, study_id)
    """
    
    agol_api: AgolAPI
    
    def __init__(self):
        self.agol_api = AgolAPI_Injector()

    async def execute(self, parcel_id: int, study_id: int):
        LOGGER.info(f'Starting Daycent executions for study {study_id} and parcel {parcel_id}.')

        # TODO get args from study parameters.
        resolution = '4km'
        interval = 'monthly'
        type = 'normals'

        wth_file_path = await BuildWeatherFile().build(parcel_id, resolution=resolution, interval=interval, type=type)

        parcel_mapunits = self.get_parcel_mapunits(parcel_id)
        LOGGER.info(f'Parcel {parcel_id} map units: {parcel_mapunits}')

        for mapunit in parcel_mapunits:
            LOGGER.info(f'Starting execution for mapunit {mapunit["id"]}.')
            with tempfile.TemporaryDirectory(suffix=f'_{study_id}_{parcel_id}') as tmpdir:
                LOGGER.info(f'Created temporary directory {tmpdir}')

                # Copy files that do not vary between executions.
                # TODO Check if linking works as well.
                self.copy_base_files(tmpdir)

                # Copy the previously generated weather file.
                shutil.copy(wth_file_path, os.path.join(tmpdir, 'site.wth'))

                build_soilsin = BuildSoilsin()
                await build_soilsin.build(tmpdir, int(mapunit['id']))

                LOGGER.info(f'Finished Daycent execution for study {study_id} and parcel {parcel_id}.')

            
    def get_parcel_mapunits(self, parcel_id: int):
        layer_ref = self.agol_api.get_layer_ref(settings.agol_base_layer_id)
        featureSet = layer_ref.query(where=f'parcel_key = {parcel_id}', return_all_records=False, result_record_count=1, out_fields=['map_unit_data'])
        map_unit_data = featureSet.features[0].attributes['map_unit_data']
        return json.loads(map_unit_data)

    def copy_base_files(self, tmpdir: str):
        for file_name in os.listdir(settings.daycent_basedir):
            source_file = os.path.join(settings.daycent_basedir, file_name)
            target_file = os.path.join(tmpdir, file_name)
            
            if os.path.isfile(source_file):
                shutil.copy(source_file, target_file)
                print(f"Copied: {file_name}")

if __name__ == '__main__':
    import asyncio
    executor = DaycentExecutor()
    asyncio.run(executor.execute(211091, 1))
