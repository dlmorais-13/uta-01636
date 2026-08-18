import logging
import traceback
from abc import ABC, abstractmethod

LOGGER = logging.getLogger(__name__)


class Job(ABC):
    """
    Abstract class for the jobs executed in the app.
    """

    name: str

    def __init__(self):
        self.name = self.__class__.__name__

    async def run(self, params: dict):
        """
        Run method to trap the actual execution in a try-except block.
        """

        try:
            LOGGER.info(f"Running job <{self.name}>")
            await self.logic(params)
        except Exception as e:
            LOGGER.error(f"Error executing job <{self.name}>: {e}")
            LOGGER.error(f"Stack: {traceback.format_exc()}")
        else:
            LOGGER.info(f"Job executed <{self.name}>")

    @abstractmethod
    async def logic(self, params: dict):
        pass
