
import logging
from abc import ABC, abstractmethod

LOGGER = logging.getLogger(__name__)


class Job(ABC):

    name: str

    def __init__(self):
        self.name = self.__class__.__name__

    async def run(self, params: dict):
        try:
            LOGGER.info(f'Running job <{self.name}>')
            await self.logic(params)
        except Exception as e:
            LOGGER.error(f'Error executing job <{self.name}>: {e}')
        else:
            LOGGER.info(f'Job executed <{self.name}>')

    @abstractmethod
    async def logic(self, params: dict):
        pass
