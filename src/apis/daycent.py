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
    Class to execute Daycent for a given parcel and simulation.

    Will create a temporary execution folder, copy all necessary static files,
    invoke the creation of the parameter files, execute the Daycent analysis,
    and upload the results into the ArcGIS online layer with simulation results data.

    Examples:

        executor = DaycentExecutor()
        await executor.execute(parcel_id, simulation_id)
    """

    agol_api: AgolAPI
    ssurgo_api: Ssurgo_API
    parcel: Feature
    params: dict

    def __init__(self):
        self.agol_api = AgolAPI_Injector()
        self.ssurgo_api = Ssurgo_API()

    async def execute(
        self, parcel_id: int, simulation_id: int, simulation_params: dict | None = None
    ):
        """
        Executes DayCent model for a given parcel and simulation.

        Args:
            parcel_id: ID of the parcel in the base layer. The OBJECTID column.
            simulation_id: ID of the simulation being processed. The OBJECTID column.
            simulation_params: The parameters of the simulation being processed.
                Optional. By default this function will load the parameters from
                the database.
        """

        LOGGER.info(
            f"Starting Daycent executions for simulation {simulation_id} and parcel {parcel_id}."
        )

        if simulation_params is None:
            simulation_table_ref = self.agol_api.get_table_ref(
                settings.agol_simulations_layer_id
            )
            simulation_query_res = simulation_table_ref.query(where=f"OBJECTID = {simulation_id}")
            simulation_obj = simulation_query_res.features[0].attributes
            simulation_params = json.loads(simulation_obj["params"])
        self.params = simulation_params

        base_layer_ref = self.agol_api.get_layer_ref(settings.agol_base_layer_id)
        query_res = base_layer_ref.query(
            where=f"parcel_key = {parcel_id}", return_geometry=True, out_sr=4326
        )
        self.parcel = query_res.features[0]

        site_elevation, wth_file_path = await BuildWeatherFile().build(
            self.parcel
        )

        parcel_mapunits = self.get_parcel_mapunits()
        LOGGER.info(f"Parcel {parcel_id} map units: {parcel_mapunits}")

        results_per_unit = dict()

        for mapunit in parcel_mapunits:
            mapunit_key = int(mapunit["id"])
            LOGGER.info(f"Starting execution for mapunit {mapunit_key}.")

            tmpdir = tempfile.mkdtemp(suffix=f"_{simulation_id}_{parcel_id}")

            try:
                LOGGER.info(f"Created temporary directory {tmpdir}")

                await self.prepare_input_files(
                    tmpdir=tmpdir,
                    params=simulation_params,
                    mapunit_key=mapunit_key,
                    site_elevation=site_elevation,
                    wth_file_path=wth_file_path,
                )

                self.execute_daycent(tmpdir)
                results_per_unit[mapunit_key] = self.read_results(
                    tmpdir, vars=["somtc", "totalc", "totsysc"]
                )

                LOGGER.info(
                    f"Finished Daycent execution for simulation {simulation_id} and parcel {parcel_id}."
                )
            except Exception as e:
                msg = f"Error in Daycent execution for simulation {simulation_id} and parcel {parcel_id}"
                LOGGER.exception(msg)
                raise Exception(msg) from e
            finally:
                if not settings.debug:
                    shutil.rmtree(tmpdir)
                else:
                    LOGGER.info(f"Not removing direction: {tmpdir}")

        results = self.aggregate_results(results_per_unit)
        self.upload_results(simulation_id=simulation_id, results=dict(results))

    async def prepare_input_files(
        self,
        tmpdir: str,
        params: dict,
        wth_file_path: str,
        mapunit_key: int,
        site_elevation: int | None,
    ):
        """
        Prepare the input files from the model execution.

        Args:
            tmpdir: The temporary folder being used for this execution.
            params: The simulation parameters.
            wth_file_path: The path for the file created with weather data.
            mapunit_key: The ID of the SSURGO map unit being processed.
            site_elevation: The elevation in the middle point of the parcel.
        """

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
            start_year=params["simulation_start_year"],
            end_year=params["simulation_end_year"],
            wth_file=wth_file_path,
        ).build()

        await BuildFixFile(dest_dir=tmpdir, soil_layer_data=soil_layer_data).build()

        await BuildScheduleFile(
            dest_dir=tmpdir,
            start_year=params["simulation_start_year"],
            end_year=params["simulation_end_year"],
        ).build()

    def get_parcel_mapunits(self) -> dict:
        """
        Gets the parcel SSURGO map units as a dict.

        Returns:
            The dictionary object with the map units data.
        """

        map_unit_data = self.parcel.attributes["map_unit_data"]
        return json.loads(map_unit_data)

    def copy_base_files(self, tmpdir: str):
        """
        Copy to the temporary work folder the files from DayCents
        base directory.
        """

        for file_name in os.listdir(settings.daycent_basedir):
            source_file = os.path.join(settings.daycent_basedir, file_name)
            target_file = os.path.join(tmpdir, file_name)

            if os.path.isfile(source_file):
                shutil.copy(source_file, target_file)

    def execute_daycent(self, tmpdir: str):
        """
        Executes the DayCent model in the working folder.

        Args:
            tmpdir: The temporary working folder.
        """

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
        """
        Executes the output coversion binary (DDlist100) in the working folder.

        Args:
            tmpdir: The temporary working folder.
        """
        
        ddlist_path = os.path.join(tmpdir, "DDlist100_rev491")
        exec(
            ddlist_path,
            ["site", "output", "outvars.txt"],
            tmpdir,
            logger=LOGGER,
            expected_output="Generating list file: output.lis",
        )

    def upload_results(self, simulation_id: int, results: dict):
        """
        Upload the results of the model execution to
        the results layer in ArcGIS Online.

        Args:
            simulation_id: ID of the simulation. OBJECTID column.
            results: The results read from the model output.
        """

        features = []
        for year in results["totalc"]:
            value = results["totalc"][year]
            features.append(
                Feature(
                    geometry=self.parcel.geometry,
                    attributes=dict(
                        parcel_key=self.parcel.attributes["parcel_key"],
                        simulation_id=simulation_id,
                        simulation_date=f"{year}-01-01",
                        carbon_stock=value,
                    ),
                )
            )

        self.agol_api.add_list(settings.agol_simulations_layer_id, features)

    def read_results(self, tmpdir: str, vars: list[str]) -> dict[dict[float]]:
        """
        Call the execution of the model's output file generation and 
        read the results into a dictionary.

        Args:
            tmpdir: The temporary working folder.
            vars: The list of variables that are going to be generated.

        Returns:
            The variables read from model's output in a nested dictionary. The
            first keys are the name of the variable, and the second keys are the
            year of the value. The values are the variables values for the given year
            as a float.
        """

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
        """
        Write the configuration file (outvars.txt) in the temporary working folder.
        The file contents are each desired output variable, one line per each.

        Args:
            tmpdir: The temporary working folder.
            vars: The list of desired output variables.
        """

        with open(os.path.join(tmpdir, "outvars.txt"), "w") as outvars_file:
            outvars_file.writelines([f"{v}\n" for v in vars])

    def aggregate_results(self, results_per_mapunit: dict):
        """
        Aggregate the results from the multiple executions of the model
        averaged by the area of each map unit compared to the total area of the parcel.

        Args:
            results_per_mapunit: The dictionary with all the output values for each map unit.
            
        Returns:
            The averaged result.
        """

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
        executor.execute(211091, 2, dict(simulation_start_year=2021, simulation_end_year=2050))
    )
