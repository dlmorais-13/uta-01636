import os
import tempfile
import shutil
import logging
import json
from collections import defaultdict
from arcgis.features import Feature
from soildb import SDAQueryError

from src.jobs.job import Job
from src.settings import settings
from src.apis.exec import exec
from src.utils.build_soilsin import BuildSoilsin
from src.utils.build_weather_file import BuildWeatherFile
from src.utils.build_site_file import BuildSiteFile
from src.utils.build_climate_change_files import BuildClimateChangeFiles
from src.utils.build_fix_file import BuildFixFile
from src.utils.build_schedule_file import BuildScheduleFile
from src.utils.management_options.ManagementOption import ExecType
from src.utils.management_options.ManagementOptionFactory import (
    get_equilibrium_management_by_basin,
)
from src.utils.management_options.CropRotation import CropRotation
from src.utils.management_options.Monoculture import Monoculture
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.ssurgo_api import Ssurgo_API
from src.models.parcel_repository import ParcelRepository
from src.apis.daymet import DaymetNetworkError

LOGGER = logging.getLogger(__name__)


class DaycentExecutor(Job):
    """
    Class to execute Daycent for a given parcel and simulation.

    Will create a temporary execution folder, copy all necessary static files,
    invoke the creation of the parameter files, execute the Daycent analysis,
    and upload the results into the ArcGIS online layer with simulation results data.
    """

    agol_api: AgolAPI
    ssurgo_api: Ssurgo_API
    parcel: Feature
    params: dict
    parcel_repository: ParcelRepository

    def __init__(self):
        super().__init__()
        self.agol_api = AgolAPI_Injector()
        self.ssurgo_api = Ssurgo_API()
        self.parcel_repository = ParcelRepository()

    async def logic(self, params: dict):
        """
        Executes DayCent model for a given parcel and simulation.

        Args:
            parcel_id: ID of the parcel in the base layer. The OBJECTID column.
            type: Type of the execution. One of "equilibrium", "base" or "simulation".
            simulation_id: ID of the simulation being processed. The OBJECTID column.
                Optional. Not required for equilibrium and base executions.
        """

        LOGGER.info(f"Starting Daycent execution with parameters {params}.")

        self.params = params
        parcel_id = self.params["parcel_id"]
        simulation_id = self.params.get("simulation_id", None)
        exec_type: ExecType = self.params["type"]

        base_layer_ref = self.agol_api.get_layer_ref(settings.agol_base_layer_id)
        query_res = base_layer_ref.query(
            where=f"parcel_key = {parcel_id}", return_geometry=True, out_sr=4326
        )
        self.parcel = query_res.features[0]

        # TODO Maybe it is necessary to change the weather file build for equilibrium and base executions.
        site_elevation, wth_file_path = await BuildWeatherFile().build(self.parcel)

        parcel_mapunits = self.get_parcel_mapunits()
        LOGGER.info(f"Parcel {parcel_id} map units: {parcel_mapunits}")

        mapunit_ids = [mu["id"] for mu in parcel_mapunits]
        if len(mapunit_ids) != len(set(mapunit_ids)):
            LOGGER.info(f"Found duplicated map units. Merging...")
            parcel_mapunits = self.merge_mapunits(parcel_mapunits)
            self.parcel_repository.update_mapunits(self.parcel, parcel_mapunits)
            LOGGER.info(f"Parcel {parcel_id} new map units: {parcel_mapunits}")

        results_per_unit = dict()
        for mapunit in parcel_mapunits:
            mapunit_key = int(mapunit["id"])
            LOGGER.info(f"Starting execution for mapunit {mapunit_key}.")

            tmpdir = tempfile.mkdtemp(
                suffix=f"_{simulation_id or exec_type}_{parcel_id}_{exec_type}"
            )

            try:
                LOGGER.info(f"Created temporary directory {tmpdir}")

                input_files_prepared = await self.prepare_input_files(
                    tmpdir=tmpdir,
                    mapunit_key=mapunit_key,
                    site_elevation=site_elevation,
                    wth_file_path=wth_file_path,
                    exec_type=exec_type,
                )

                if input_files_prepared:
                    self.execute_daycent(tmpdir, mapunit_key)

                    if exec_type == "simulation":
                        results_per_unit[mapunit_key] = self.read_results(
                            tmpdir, vars=["somtc", "totalc", "totsysc"]
                        )
                    else:
                        ext_file_name = f"{exec_type}_{mapunit_key}.100"
                        txt_file_name = f"{ext_file_name}.txt"
                        shutil.copyfile(
                            os.path.join(tmpdir, ext_file_name),
                            os.path.join(tmpdir, txt_file_name),
                        )

                        self.parcel_repository.upload_attachment(
                            parcel=self.parcel,
                            file_path=os.path.join(tmpdir, txt_file_name),
                            keywords=f"{exec_type}:{mapunit_key}",
                        )

                    LOGGER.info(
                        f"Finished Daycent execution for simulation {simulation_id}, parcel {parcel_id}, and map unit {mapunit_key}."
                    )

                else:
                    LOGGER.info(
                        f"Daycent not executed for simulation {simulation_id}, parcel {parcel_id}, and map unit {mapunit_key}. Not enough data to prepare input files."
                    )
                    self.parcel_repository.mark_map_unit_as_unusable(
                        parcel=self.parcel, map_unit_id=mapunit_key
                    )
            except SDAQueryError as e:
                msg = f"Error in Daycent execution for simulation {simulation_id}, parcel {parcel_id}, and map unit {mapunit_key}: Probably network error"
                LOGGER.exception(msg)
                raise DaycentExecutionNetworkError(msg) from e
            except Exception as e:
                msg = f"Error in Daycent execution for simulation {simulation_id}, parcel {parcel_id}, and map unit {mapunit_key}"
                LOGGER.exception(msg)
                raise Exception(msg) from e
            finally:
                if not settings.debug:
                    shutil.rmtree(tmpdir)
                else:
                    LOGGER.info(f"Not removing directory: {tmpdir}")

        if exec_type == "simulation":
            results = self.aggregate_results(results_per_unit)
            self.upload_results(simulation_id=simulation_id, results=dict(results))

    def merge_mapunits(self, parcel_mapunits: list[dict]) -> list[dict]:
        """
        Merge the map units in the list by their ID, summing the area as necessary.

        Args:
            parcel_mapunits: The list of map units to merge.

        Returns:
            The merged list of map units.
        """
        result = []
        for mu in parcel_mapunits:
            rmu = next((rmu for rmu in result if rmu["id"] == mu["id"]), None)
            if rmu is None:
                result.append(mu)
            else:
                rmu["area"] += mu["area"]
        return result

    async def prepare_input_files(
        self,
        tmpdir: str,
        wth_file_path: str,
        mapunit_key: int,
        site_elevation: int | None,
        exec_type: ExecType,
    ):
        """
        Prepare the input files from the model execution.

        Args:
            tmpdir: The temporary folder being used for this execution.
            params: The simulation parameters.
            wth_file_path: The path for the file created with weather data.
            mapunit_key: The ID of the SSURGO map unit being processed.
            site_elevation: The elevation in the middle point of the parcel.

        Returns:
            True if there is enough data to prepare the minimum required
            input files, False otherwise.
        """

        # Copy files that do not vary between executions.
        # TODO: Check if linking works instead of copy for daycent input files, except fix.100.
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

        if soil_layer_data is None:
            return False

        await BuildSiteFile(
            dest_dir=tmpdir,
            parcel=self.parcel,
            nlayers=len(soil_layer_data),
            elevation=site_elevation,
            components=components,
        ).build()

        if exec_type == "simulation":
            await BuildClimateChangeFiles(
                dest_dir=tmpdir,
                start_year=self.params["start_year"],
                end_year=self.params["end_year"],
                wth_file=wth_file_path,
            ).build()

        await BuildFixFile(dest_dir=tmpdir, soil_layer_data=soil_layer_data).build()

        if exec_type == "equilibrium":
            management_option = get_equilibrium_management_by_basin(
                self.parcel.attributes["basin"],
                self.params["start_year"],
                self.params["end_year"],
                {},
            )
        elif exec_type == "base":
            # TODO Parametrize this.
            management_option = CropRotation(
                exec_type,
                self.params["start_year"],
                self.params["end_year"],
                {"crop": ["C1", "ALF"], "fert": "UREA", "cult": "K", "harv": "G90S"},
            )

            # Download equilibrium attachments.
            self.download_attachments(tmpdir, "equilibrium", mapunit_key)
        else:
            # TODO Parametrize this.
            management_option = CropRotation(
                exec_type,
                self.params["start_year"],
                self.params["end_year"],
                {
                    "crop": ["C1", "SYBN", "SYBN", "SYBN", "ALF"],
                    "fert": "UREA",
                    "cult": "K",
                    "harv": "G90S",
                },
            )

            # Download base attachments.
            self.download_attachments(tmpdir, "base", mapunit_key)

        await BuildScheduleFile(
            dest_dir=tmpdir,
            start_year=self.params["start_year"],
            end_year=self.params["end_year"],
            management=management_option,
        ).build()

        return True

    def get_parcel_mapunits(self) -> dict:
        """
        Gets the parcel SSURGO map units as a dict.

        Returns:
            The dictionary object with the map units data.
        """

        map_unit_data = self.parcel.attributes["map_unit_data"]
        return json.loads(map_unit_data)

    def download_attachments(self, tmpdir: str, type: ExecType, mapunit_key: int):
        """
        Download the attachments necessary for the extended DayCent execution.

        Args:
            tmpdir: Temporary working folder to save the attachment.
            type: Type of the execution of the attachment. Should be the
                type before the current execution. "base" for "simulation"
                and "equilibrium" for "base".
            mapunit_key: ID of the map unit to get the attachment.
        """

        attachments = self.agol_api.get_attachments(
            settings.agol_base_layer_id, self.parcel.attributes["OBJECTID"]
        )
        keyword = f"{type}:{mapunit_key}"
        for a in attachments:
            if a["keywords"] == keyword:
                self.agol_api.download_attachment(
                    settings.agol_base_layer_id,
                    self.parcel.attributes["OBJECTID"],
                    a["id"],
                    tmpdir,
                )
                shutil.move(
                    os.path.join(tmpdir, f"{type}_{mapunit_key}.100.txt"),
                    os.path.join(tmpdir, f"{type}_{mapunit_key}.100"),
                )

    def copy_base_files(self, tmpdir: str):
        """
        Copy to the temporary work folder the files from DayCents
        base directory.

        Args:
            tmpdir: Temporary working folder to save the attachment.
        """

        for file_name in os.listdir(settings.daycent_basedir):
            source_file = os.path.join(settings.daycent_basedir, file_name)
            target_file = os.path.join(tmpdir, file_name)

            if os.path.isfile(source_file):
                shutil.copy(source_file, target_file)

    def execute_daycent(self, tmpdir: str, mapunit_key: int):
        """
        Executes the DayCent model in the working folder.

        Args:
            tmpdir: The temporary working folder.
            mapunit_key: ID of the map unit being processed.
        """

        daycent_path = os.path.join(tmpdir, "DDcentEVI_rev491")

        match self.params["type"]:
            case "simulation":
                args = [
                    "-s",
                    "site",
                    "--site",
                    f"base_{mapunit_key}.100",
                ]
            case "base":
                args = [
                    "-s",
                    "site",
                    "-W",
                    f'{self.params["type"]}_{mapunit_key}',
                    "--site",
                    f"equilibrium_{mapunit_key}.100",
                ]
            case "equilibrium":
                args = ["-s", "site", "-W", f'{self.params["type"]}_{mapunit_key}']

        exec(
            daycent_path,
            args,
            tmpdir,
            logger=LOGGER,
            expected_output="Execution success",
        )

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

        # Disconsider any mapunit without computed data.
        mapunits_with_data = [
            mapunit
            for mapunit in parcel_mapunits
            if int(mapunit["id"]) in results_per_mapunit
        ]

        total_area = sum([float(mapunit["area"]) for mapunit in mapunits_with_data])

        for mapunit in mapunits_with_data:
            mapunit_results = results_per_mapunit[int(mapunit["id"])]
            for var in mapunit_results:
                for year in mapunit_results[var]:
                    results[var][year] += (
                        mapunit_results[var][year] * float(mapunit["area"]) / total_area
                    )

        return results


class DaycentExecutionNetworkError(Exception):
    """Raised when a network error is identified during the execution."""

    pass


# Execution of equilibrium calculation of all parcels.
if __name__ == "__main__":
    import asyncio
    import traceback

    execution = os.environ["EXECUTOR_MODE"] if "EXECUTOR_MODE" in os.environ else "all"

    # TODO Base for parcel 58527 encountered random errors.
    # It is necessary to do something about it (retries?).

    if execution == "all":
        agol_api = AgolAPI_Injector()
        base_layer = agol_api.get_layer_ref(settings.agol_base_layer_id)
        parcel_repository = ParcelRepository()
        executor_mod = int(os.environ["EXECUTOR_MOD"])
        executor_qty = int(os.environ["EXECUTOR_QTY"])
        executor_limit = (
            int(os.environ["EXECUTOR_LIMIT"])
            if "EXECUTOR_LIMIT" in os.environ
            else None
        )

        count = 0
        while True:
            try:
                query_res = base_layer.query(
                    where=f"""
                        equilibrium_calculated = 0
                        AND MOD(parcel_key, {executor_qty}) = {executor_mod}
                    """,
                    out_fields=["OBJECTID", "parcel_key", "map_unit_data"],
                    return_geometry=False,
                    result_record_count=1,
                )

                if not len(query_res):
                    break

                parcel = query_res.features[0]

                executor = DaycentExecutor()
                asyncio.run(
                    executor.logic(
                        dict(
                            parcel_id=parcel.attributes["parcel_key"],
                            start_year=1,
                            end_year=5000,
                            type="equilibrium",
                        )
                    )
                )

            except (DaycentExecutionNetworkError, DaymetNetworkError) as ne:
                LOGGER.exception(
                    f"Network error when running Daycent equilibrium for parcel {parcel}"
                )
                try:
                    parcel_repository.mark_parcel_as_precalc_error(
                        parcel, "equilibrium", 3
                    )
                except Exception as e2:
                    LOGGER.error(
                        f'Error trying to set parcel {parcel.attributes["parcel_key"]} as error.'
                    )
                    traceback.print_exc()
            except Exception as e:
                LOGGER.error(
                    f"Error running DayCent equilibrium for parcel {parcel.attributes['parcel_key']}"
                )
                traceback.print_exc()
                try:
                    parcel_repository.mark_parcel_as_precalc_error(
                        parcel, "equilibrium"
                    )
                except Exception as e2:
                    LOGGER.error(
                        f'Error trying to set parcel {parcel.attributes["parcel_key"]} as error.'
                    )
                    traceback.print_exc()

            count += 1
            if executor_limit is not None and count >= executor_limit:
                break

    elif execution == "reprocess":
        agol_api = AgolAPI_Injector()
        base_layer = agol_api.get_layer_ref(settings.agol_base_layer_id)
        parcel_repository = ParcelRepository()

        try:
            query_res = base_layer.query(
                where="equilibrium_calculated >= 2",
                out_fields=["OBJECTID", "parcel_key", "map_unit_data"],
                return_geometry=False,
                result_record_count=1,
            )

            if len(query_res):
                parcel = query_res.features[0]
                executor = DaycentExecutor()
                asyncio.run(
                    executor.logic(
                        dict(
                            parcel_id=parcel.attributes["parcel_key"],
                            start_year=1,
                            end_year=5000,
                            type="equilibrium",
                        )
                    )
                )
            else:
                LOGGER.info("No parcel found to reprocess.")

        except (DaycentExecutionNetworkError, DaymetNetworkError) as ne:
            LOGGER.exception(
                f"Network error when running Daycent equilibrium for parcel {parcel}"
            )
            try:
                parcel_repository.mark_parcel_as_precalc_error(parcel, "equilibrium", 3)
            except Exception as e2:
                LOGGER.error(
                    f'Error trying to set parcel {parcel.attributes["parcel_key"]} as error.'
                )
                traceback.print_exc()
        except Exception as e:
            LOGGER.error(
                f"Error running DayCent equilibrium for parcel {parcel.attributes['parcel_key']}"
            )
            traceback.print_exc()
            try:
                parcel_repository.mark_parcel_as_precalc_error(parcel, "equilibrium")
            except Exception as e2:
                LOGGER.error(
                    f'Error trying to set parcel {parcel.attributes["parcel_key"]} as error.'
                )
                traceback.print_exc()

    elif execution == "equilibrium":
        executor = DaycentExecutor()
        asyncio.run(
            executor.logic(
                dict(
                    parcel_id=194253,
                    start_year=1,
                    end_year=5000,
                    type="equilibrium",
                )
            )
        )

    elif execution == "base":
        executor = DaycentExecutor()
        asyncio.run(
            executor.logic(
                dict(
                    parcel_id=66491,
                    start_year=1850,
                    end_year=2025,
                    type="base",
                )
            )
        )

    elif execution == "simulation":
        executor = DaycentExecutor()
        asyncio.run(
            executor.logic(
                dict(
                    parcel_id=211136,
                    simulation_id=16,
                    start_year=2026,
                    end_year=2026 + 50,
                    type="simulation",
                )
            )
        )
