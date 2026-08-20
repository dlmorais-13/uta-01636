from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.jobs.job import Job
import logging

LOGGER = logging.getLogger(__name__)


class ProcessCreatedSimulation(Job):
    """
    Job class to process simulations that are newly created.
    """

    api: AgolAPI

    async def logic(self, params: dict):
        LOGGER.info(f'Executing job ProcessCreatedSimulation for simulation #{params["simulation_id"]}')
        self.api = AgolAPI_Injector()

        


if __name__ == "__main__":
    import asyncio

    asyncio.run(ProcessCreatedSimulation().logic({"simulation_id": 12}))
