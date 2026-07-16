import os
import tempfile
import shutil
import logging
import json
from functools import reduce
from collections import defaultdict
from arcgis.features import Feature

from src.settings import settings
from src.apis.exec import exec
from src.utils.build_soilsin import BuildSoilsin
from src.utils.build_weather_file import BuildWeatherFile
from src.utils.build_site_file import BuildSiteFile
from src.utils.build_climate_change_files import BuildClimateChangeFiles
from src.utils.build_fix_file import BuildFixFile
from src.utils.build_schedule_file import BuildScheduleFile
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.ssurgo_api import Ssurgo_API

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
    parcel: Feature
    params: dict

    def __init__(self):
        self.agol_api = AgolAPI_Injector()
        self.ssurgo_api = Ssurgo_API()

    async def execute(
        self, parcel_id: int, study_id: int, study_params: dict | None = None
    ):
        LOGGER.info(
            f"Starting Daycent executions for study {study_id} and parcel {parcel_id}."
        )

        if study_params is None:
            study_table_ref = self.agol_api.get_table_ref(
                settings.agol_studies_layer_id
            )
            study_query_res = study_table_ref.query(where=f"study_id = {study_id}")
            study_obj = study_query_res.features[0].attributes
            study_params = json.loads(study_obj["params"])
        self.params = study_params

        base_layer_ref = self.agol_api.get_layer_ref(settings.agol_base_layer_id)
        query_res = base_layer_ref.query(
            where=f"parcel_key = {parcel_id}", return_geometry=True, out_sr=4326
        )
        self.parcel = query_res.features[0]

        site_elevation, wth_file_path = await BuildWeatherFile().build_daymet(
            self.parcel
        )

        parcel_mapunits = self.get_parcel_mapunits()
        LOGGER.info(f"Parcel {parcel_id} map units: {parcel_mapunits}")

        results_per_unit = dict()

        for mapunit in parcel_mapunits:
            mapunit_key = int(mapunit["id"])
            LOGGER.info(f"Starting execution for mapunit {mapunit_key}.")

            tmpdir = tempfile.mkdtemp(suffix=f"_{study_id}_{parcel_id}")

            try:
                LOGGER.info(f"Created temporary directory {tmpdir}")

                await self.prepare_input_files(
                    tmpdir=tmpdir,
                    params=study_params,
                    mapunit_key=mapunit_key,
                    site_elevation=site_elevation,
                    wth_file_path=wth_file_path,
                )

                self.execute_daycent(tmpdir)
                results_per_unit[mapunit_key] = self.read_results(
                    tmpdir, vars=["somtc", "totalc", "totsysc"]
                )

                LOGGER.info(
                    f"Finished Daycent execution for study {study_id} and parcel {parcel_id}."
                )
            except Exception as e:
                LOGGER.exception(
                    f"Error in Daycent execution for study {study_id} and parcel {parcel_id}"
                )
            finally:
                if not settings.debug:
                    shutil.rmtree(tmpdir)
                else:
                    LOGGER.info(f"Not removing direction: {tmpdir}")

        results = self.aggregate_results(results_per_unit)
        self.upload_results(study_id=study_id, results=dict(results))

    async def prepare_input_files(
        self,
        tmpdir: str,
        params: dict,
        wth_file_path: str,
        mapunit_key: int,
        site_elevation: int | None,
    ):
        # Copy files that do not vary between executions.
        # TODO: Check if linking works instead of copy for daycent input files, except fix.100. kanpilotID(aop861yphyqkvfn2x9xpdkf5)
        self.copy_base_files(tmpdir)

        # Copy the previously generated weather file.
        shutil.copy(wth_file_path, os.path.join(tmpdir, "site.wth"))

        # Get the SSURGO components for the map unit. They are used by multiple inputs.
        components = await self.ssurgo_api.get_ssurgo_components(
            mapunit_key, extra_columns=["slope_r"]
        )

        soil_layer_data = await BuildSoilsin(tmpdir).build(
            mapunit_key, components=components
        )

        await BuildSiteFile(
            dest_dir=tmpdir,
            parcel=self.parcel,
            nlayers=len(soil_layer_data),
            elevation=site_elevation,
            components=components,
        ).build()

        await BuildClimateChangeFiles(
            dest_dir=tmpdir,
            start_year=params["study_start_year"],
            end_year=params["study_end_year"],
            wth_file=wth_file_path,
        ).build()

        await BuildFixFile(dest_dir=tmpdir, soil_layer_data=soil_layer_data).build()

        await BuildScheduleFile(
            dest_dir=tmpdir,
            start_year=params["study_start_year"],
            end_year=params["study_end_year"],
        ).build()

    def get_parcel_mapunits(self):
        map_unit_data = self.parcel.attributes["map_unit_data"]
        return json.loads(map_unit_data)

    def copy_base_files(self, tmpdir: str):
        for file_name in os.listdir(settings.daycent_basedir):
            source_file = os.path.join(settings.daycent_basedir, file_name)
            target_file = os.path.join(tmpdir, file_name)

            if os.path.isfile(source_file):
                shutil.copy(source_file, target_file)

    def execute_daycent(self, tmpdir: str):
        # TODO Check if the execution succeeded.
        daycent_path = os.path.join(tmpdir, "DDcentEVI_rev491")
        # return_code = exec(daycent_path, ["-s", "site", "-N", "site"], self.workingDir, logger=LOGGER)
        return_code = exec(
            daycent_path,
            ["-s", "site"],
            tmpdir,
            logger=LOGGER,
            expected_output="Execution success",
        )
        print(return_code)

    def execute_ddlist(self, tmpdir: str):
        # TODO Check if the execution succeeded.
        ddlist_path = os.path.join(tmpdir, "DDlist100_rev491")
        exec(
            ddlist_path,
            ["site", "output", "outvars.txt"],
            tmpdir,
            logger=LOGGER,
            expected_output="Generating list file: output.lis",
        )

    def upload_results(self, study_id: int, results: dict):
        features = []
        for year in results["totalc"]:
            value = results["totalc"][year]
            features.append(
                Feature(
                    geometry=self.parcel.geometry,
                    attributes=dict(
                        parcel_key=self.parcel.attributes["parcel_key"],
                        study_id=study_id,
                        simulation_date=f"{year}-01-01",
                        carbon_stock=value,
                    ),
                )
            )

        self.agol_api.add_list(settings.agol_studies_layer_id, features)

    def read_results(self, tmpdir: str, vars: list[str]):
        self.write_outvars(tmpdir, vars)
        self.execute_ddlist(tmpdir)

        with open(os.path.join(tmpdir, "output.lis"), "r") as output_file:
            # Skip first line
            next(output_file)

            headers = next(output_file)
            var_pos = dict()
            for index, value in enumerate(headers.split()):
                var_pos[value] = index

            # Skip empty line
            next(output_file)

            # Read the output
            output = defaultdict(lambda: defaultdict(float))
            for line in output_file:
                values = line.split()
                year = values[var_pos["time"]].split(".")[0]
                for v in vars:
                    output[v][year] = float(values[var_pos[v]])

            return output

    def write_outvars(self, tmpdir: str, vars: list[str]):
        with open(os.path.join(tmpdir, "outvars.txt"), "w") as outvars_file:
            outvars_file.writelines([f"{v}\n" for v in vars])

    def aggregate_results(self, results_per_mapunit: dict):
        results = defaultdict(lambda: defaultdict(float))
        parcel_mapunits = self.get_parcel_mapunits()

        total_area = sum([float(mapunit["area"]) for mapunit in parcel_mapunits])

        for mapunit in parcel_mapunits:
            mapunit_results = results_per_mapunit[int(mapunit["id"])]
            for var in mapunit_results:
                for year in mapunit_results[var]:
                    results[var][year] += (
                        mapunit_results[var][year] * float(mapunit["area"]) / total_area
                    )

        return results


if __name__ == "__main__":
    import asyncio

    executor = DaycentExecutor()
    asyncio.run(
        executor.execute(211091, 1, dict(study_start_year=2021, study_end_year=2050))
    )
