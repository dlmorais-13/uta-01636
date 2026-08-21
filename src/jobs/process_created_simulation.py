import logging
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
        self.api = AgolAPI_Injector()
        self.simulation = SimulationRepository().get_simulation(params["simulation_id"])
        parcels = ParcelRepository().get_parcels(self.build_where_clause_from_filters(self.simulation['filters']))

        survey_last_year = self.api.get_latest_survey_year()
        job_manager = JobManager()

        # TODO Remove the index to process all parcels
        for p in parcels[:10]:
            job_manager.add(
                name=f'jobs.daycent.DaycentExecutor:{params["simulation_id"]}_{p.attributes["parcel_key"]}',
                params={
                    "parcel_id": p.attributes["parcel_key"],
                    "simulation_id": params["simulation_id"],
                    "start_year": survey_last_year + 1,
                    "end_year": survey_last_year + 50
                }
            )
            

    def build_where_clause_from_filters(self, filters) -> str:
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
            clauses_per_filter.setdefault(f['name'], [])
            clauses_per_filter[f['name']].append(f"{f.get('column') or f.get('name')} = '{f['value']}'")

        last_survey_year = self.api.get_latest_survey_year()
        where = f"survey_year = '{last_survey_year}'"
        for filter_clauses in clauses_per_filter.values():
            clause = " OR ".join(filter_clauses)
            where += f" AND ({clause}) "
        return where


if __name__ == "__main__":
    import asyncio

    asyncio.run(ProcessCreatedSimulation().logic({"simulation_id": 16}))
