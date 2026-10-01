import logging
import random
from typing import Literal
from arcgis.features import Feature

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.jobs.job import Job
from src.jobs.job_manager import JobManager
from src.models.simulation_repository import SimulationRepository
from src.models.parcel_repository import ParcelRepository

LOGGER = logging.getLogger(__name__)


class ProcessCreatedSimulation(Job):
    """
    Job class to process simulations that are newly created.

    This job will calculate and create other jobs that are going to
    effectively run the calculations required to complete the simulation.
    """

    api: AgolAPI
    simulation: dict
    parcels_changes: dict[str, list] = {}

    def __init__(self):
        super().__init__()
        self.api = AgolAPI_Injector()

    async def logic(self, params: dict):
        """
        Executes the job.

        Args:
            params: The job parameters as a dict with the following keys.
                - simulation_id: The ID of the simulation to process.
        """

        LOGGER.info(
            f'Executing job ProcessCreatedSimulation for simulation #{params["simulation_id"]}'
        )
        self.simulation = SimulationRepository().get_simulation(params["simulation_id"])
        parcels = ParcelRepository().get_parcels(
            self._build_where_clause_from_filters(self.simulation["filters"])
        )

        survey_last_year = self.api.get_latest_survey_year()
        job_manager = JobManager()

        self._update_parcels_using_parameters(parcels, self.simulation["params"])

        jobs_to_add = []
        for p in parcels:
            parcel_params = {
                "parcel_id": p.attributes["parcel_key"],
                "type": "simulation",
                "simulation_id": params["simulation_id"],
                "start_year": survey_last_year + 1,
                "end_year": survey_last_year + 50,
                "changes": self.parcels_changes.get(p.attributes["parcel_key"]),
            }

            jobs_to_add.append(
                {
                    "name": f'jobs.daycent.DaycentExecutor:{params["simulation_id"]}_{p.attributes["parcel_key"]}',
                    "params": parcel_params,
                }
            )

        job_manager.add_jobs(jobs_to_add)

    def _update_parcels_using_parameters(
        self, parcels: list[Feature], parameters: list[dict]
    ) -> dict[str, list]:
        """
        Updates the list of parcels in the simulation to match
        the configured parameters.

        Args:
            parcels: The list of parcels available for this simulation.
            parameters: The list of parameters configured in the simulation.

        Returns:
            A dict with all the changes performed for each parcel.
        """

        processed_params: list[dict] = []

        for param in parameters:
            if param["type"] == "target":
                target = param["target"]
                current = self._get_current_param_value(param, parcels)
                direction = (
                    "-" if target < current else "+" if target > current else None
                )

                while True:
                    change = self._update_random_parcel(
                        param, parcels, direction, processed_params
                    )
                    self.parcels_changes.setdefault(change["parcel_key"], [])
                    self.parcels_changes.get(change["parcel_key"]).append(change)

                    current = self._get_current_param_value(param, parcels)

                    if direction == "-" and target >= current:
                        break
                    elif direction == "+" and target <= current:
                        break

                processed_params.append(param)

    def _get_current_param_value(self, param: dict, parcels: list[Feature]) -> float:
        """
        Get the current percentual value of the current parameter as they
        are defined in the parcels.

        Args:
            param: The parameter currently being processed.
            parcels: The list of parcels available for this simulation.
        """

        parcels_of_param = len(
            [p for p in parcels if p.attributes[param["column"]] == param["value"]]
        )
        return parcels_of_param / len(parcels)

    def _is_parcel_processed_for_column(self, parcel: Feature, column: str):
        """
        Indicates whether a parcel was already changed for a specific column value.

        Args:
            parcel: The parcel to look for.
            column: The column to check.

        Returns:
            True if the parcel was already changed for the column, False otherwise.
        """

        return (
            parcel.attributes["parcel_key"] in self.parcels_changes
            and next(
                (
                    c
                    for c in self.parcels_changes[parcel.attributes["parcel_key"]]
                    if c["column"] == column
                ),
                None,
            )
            is not None
        )

    def _update_random_parcel(
        self,
        param: dict,
        parcels: list[Feature],
        direction: Literal["+", "-"],
        processed_params: list[dict],
    ) -> dict:
        """
        Updates a random parcel in order to go towards the goal defined by the parameter.

        Args:
            param: The parameter being processed.
            parcels: The list of parcels available for this simulation.
            direction: The change direction of the current parameter.
                "+" means more parcels with the parameter value must be defined.
                "-" means less parcels with the parameter value must exist.
            processed_params: The list of parameters already processed.

        Returns:
            A dict with the information regarding the change.
        """

        if direction == "-":
            parcels_available_to_change = [
                p
                for p in parcels
                if p.attributes[param["column"]] == param["value"]
                and not self._is_parcel_processed_for_column(p, param["column"])
            ]

            # Chooses any value different from the current value and also different
            # from any value already processed for the same column.
            new_value = random.choice(
                [
                    p.attributes[param["column"]]
                    for p in parcels
                    if p.attributes[param["column"]]
                    not in (
                        [
                            pr["value"]
                            for pr in processed_params
                            if pr["column"] == param["column"]
                        ]
                        + [param["value"]]
                    )
                ]
            )

        else:
            parcels_available_to_change = [
                p
                for p in parcels
                if p.attributes[param["column"]] != param["value"]
                and not self._is_parcel_processed_for_column(p, param["column"])
            ]

            # Uses the value defined in the parameter.
            new_value = param["value"]

        parcel = random.choice(parcels_available_to_change)
        parcel.attributes[param["column"]] = new_value

        return {
            "parcel_key": parcel.attributes["parcel_key"],
            "column": param["column"],
            "value": new_value,
        }

    def _build_where_clause_from_filters(self, filters: list[dict]) -> str:
        """
        Builds a where clause to be used when searching the base layer, according to the
        provided filters.

        Args:
            filters: Filters to build the where clause.

        Returns:
            String with the built where clause.
        """

        clauses_per_filter: dict[str, list[str]] = {}
        for f in filters:
            clauses_per_filter.setdefault(f["name"], [])
            clauses_per_filter[f["name"]].append(
                f"{f.get('column') or f.get('name')} = '{f['value']}'"
            )

        last_survey_year = self.api.get_latest_survey_year()
        where = f"survey_year = '{last_survey_year}'"
        for filter_clauses in clauses_per_filter.values():
            clause = " OR ".join(filter_clauses)
            where += f" AND ({clause}) "
        return where


if __name__ == "__main__":
    import asyncio

    asyncio.run(ProcessCreatedSimulation().logic({"simulation_id": 17}))
