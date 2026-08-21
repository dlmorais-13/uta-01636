import json
from enum import Enum
from arcgis.features import Table, Feature

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings
from src.utils.date_utils import Agol_Now


class SimulationColumns(Enum):
    """
    Columns present in the ArcGIS Online table for the list of simulations.
    To access the column name use the value of the enum (e.g.: SimulationColumns.PARAMETERS.value)
    """

    OBJECTID = "OBJECTID"
    """Primary key."""

    PARAMETERS = "params"
    """The list of parameters in the simulation."""

    FILTERS = "filters"
    """The list of filters for the simulation."""

    OWNER = "owner"
    """The identifier of the user who created the simulation."""

    STATUS = "status"
    """The status of the simulation."""

    CREATED_DATE = "created_date"
    """Date when the simulation was created."""

    COMPLETED_DATE = "completed_date"
    """Date when all of the simulations calculations were completed."""


class SimulationStatus(Enum):
    """
    Possible statuses for a simulation in a given time.
    """

    CREATED = "created"
    """The simulation was just created and its initial processing was not done yet."""

    IN_PROGRESS = "in_progress"
    """The simulation's jobs were created and are currently available for execution."""

    COMPLETED = "completed"
    """All of the simulation's jobs were executed and it is available for analysis."""

    FAILED = "failed"
    """Some of the simulation's jobs failed to be executed."""


class SimulationRepository:
    """
    Repository class to access simulations data.
    Linked to object "UTA01636 Simulations > Simulation List" in ArcGIS Online.
    """

    api: AgolAPI
    table_ref: Table

    def __init__(self):
        self.api = AgolAPI_Injector()
        self.table_ref = self.api.get_table_ref(settings.agol_simulations_layer_id)

    def _feature_to_dict(self, feature: Feature) -> dict:
        """
        Transforms a feature fetched from AGOL into a dict.

        Args:
            feature: The feature to transform.

        Returns:
            The feature transformed into a dict.
        """
        return {
            **feature.attributes,
            "filters": json.loads(feature.attributes["filters"]),
            "params": json.loads(feature.attributes["params"]),
        }

    def _dict_to_feature(self, attributes: dict) -> Feature:
        """
        Transforms a dict into a feature in the expected format in AGOL.

        Args:
            attributes: The attributes to add to the transformed feature.

        Returns:
            The feature transformed from the parameters.
        """

        filters = json.dumps(attributes["filters"] or [])
        del attributes["filters"]
        params = json.dumps(attributes["params"] or [])
        del attributes["params"]

        return Feature(attributes=dict(**attributes, filters=filters, params=params))

    def get_simulation(self, simulation_id: int) -> dict:
        """
        Retrieves a simulation using its ID.

        Args:
            simulation_id: The ID of the simulation to retrieve.

        Returns:
            The retrieved simulation.
        """
        simulation = self.api.get_by_id(self.table_ref, simulation_id)
        return self._feature_to_dict(simulation)

    def list_simulations(self) -> list[dict]:
        """
        Lists all simulations.

        Returns:
            The list of all the simulations.
        """
        simulations = self.table_ref.query(
            where="1=1",
            return_all_records=True,
        )

        return [self._feature_to_dict(f) for f in simulations.features]

    def create_simulation(
        self, filters: list[dict] = [], parameters: list[dict] = []
    ) -> dict:
        """
        Creates a new simulation.

        Args:
            filters: List of filters for the simulation.
            parameters: List of parameters for the simulation.

        Returns:
            The created simulation.
        """

        result = self.api.add_list(
            self.table_ref,
            [
                self._dict_to_feature(
                    dict(
                        filters=filters,
                        params=parameters,
                        owner="a02462576@usu.edu_usuonline",
                        status="created",
                        created_date=Agol_Now(),
                    )
                )
            ],
        )

        simulation_id = result[0]["objectId"]
        return self.get_simulation(simulation_id)
