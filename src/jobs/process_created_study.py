from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.jobs.job import Job
import logging

LOGGER = logging.getLogger(__name__)


class ProcessCreatedStudy(Job):

    api: AgolAPI

    async def logic(self, params: dict):
        LOGGER.info(f'Executing job ProcessCreatedStudy for Study #{params["study_id"]}')
        self.api = AgolAPI_Injector()

        


if __name__ == "__main__":
    import asyncio

    asyncio.run(ProcessCreatedStudy().logic({"study_id": 12}))
