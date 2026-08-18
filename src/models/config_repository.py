from enum import Enum
from arcgis.features import Table, FeatureSet
from pydantic import BaseModel

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings


class ConfigColumns(Enum):
    """
    Columns present in the ArcGIS Online table for the list of configurations.
    To access the column name use the value of the enum (e.g.: ConfigColumns.CONFIG.value)
    """

    OBJECTID = "OBJECTID"
    """Primary key."""

    NAME = "NAME"
    """Name of the configuration."""

    CONFIG = "CONFIG"
    """Value of the configuration."""


class Config(BaseModel):
    """
    Config type to comunicate with frontend.
    """

    name: str
    config: str


class ConfigRepository:
    """
    Repository class to access data related to the system configuration.
    """

    api: AgolAPI
    table_ref: Table

    _config_cache: FeatureSet | None = None
    """Cache for the system configuration values."""

    def __init__(self):
        self.api = AgolAPI_Injector()
        self.table_ref = self.api.get_table_ref(settings.agol_config_table_id)

    def get_config(self, name: str) -> str:
        """
        Gets the value of a configuration using its name.

        Args:
            name: Name of the configuration.

        Returns:
            The configuration value.
        """

        if self._config_cache is None:
            self._config_cache = self.table_ref.query()

        config = next(
            (
                c
                for c in self._config_cache.features
                if c.attributes[ConfigColumns.NAME.value] == name
            ),
            None,
        )
        if config is None:
            raise RuntimeError(f"Config not found with name {name}")
        return config.attributes[ConfigColumns.CONFIG.value]

    def get_configs(self, prefix: str = "") -> dict:
        """
        Gets the values of all configurations having a common prefix.

        Args:
            prefix: The prefix to look for. Optional. Default to empty string.

        Returns:
            A dictionary with keys being the configuration name and value being
            their respective values.
        """

        if self._config_cache is None:
            self._config_cache = self.table_ref.query()

        return {
            c.attributes[ConfigColumns.NAME.value]: c.attributes[
                ConfigColumns.CONFIG.value
            ]
            for c in self._config_cache.features
            if c.attributes[ConfigColumns.NAME.value].startswith(prefix)
        }

    def update_configs(self, desired_configs: list[Config]):
        """
        Updates the system configuration using the list from arguments to
        update, add, and/or delete configurations as needed.

        Args:
            desired_configs: The list of the configurations in the way
                they are going to be after the operation.
        """

        allConfigs = self.table_ref.query()

        deleteList = []
        editList = []
        addList = []
        existingConfigs = []

        for config in allConfigs.features:
            configName = config.attributes[ConfigColumns.NAME.value]
            existingConfigs.append(configName)

            # Returns the first dictionary with a name == configName
            desiredValue = next(
                (dc.config for dc in desired_configs if dc.name == configName), None
            )

            if desiredValue is None:
                deleteList.append(config)
            else:
                config.attributes[ConfigColumns.CONFIG.value] = desiredValue
                editList.append(config)

        newDesiredConfigs = [
            dc for dc in desired_configs if dc.name not in existingConfigs
        ]
        for dc in newDesiredConfigs:
            addList.append(
                {
                    "attributes": {
                        ConfigColumns.NAME.value: dc.name,
                        ConfigColumns.CONFIG.value: dc.config,
                    }
                }
            )

        self.table_ref.edit_features(adds=addList, updates=editList, deletes=deleteList)
