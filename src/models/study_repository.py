import json
from enum import Enum
from arcgis.features import Table, Feature

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.settings import settings
from src.utils.date_utils import Agol_Now


class StudyColumns(Enum):
    """
    Columns present in the ArcGIS Online table for the list of studies.
    To access the column name use the value of the enum (e.g.: StudyColumns.PARAMETERS.value)
    """

    OBJECTID = "OBJECTID"
    """Primary key."""

    PARAMETERS = "params"
    """The list of parameters in the study."""

    FILTERS = "filters"
    """The list of filters for the study."""

    OWNER = "owner"
    """The identifier of the user who created the study."""

    STATUS = "status"
    """The status of the study."""

    CREATED_DATE = "created_date"
    """Date when the study was created."""

    COMPLETED_DATE = "completed_date"
    """Date when all of the studies calculations were completed."""


class StudyStatus(Enum):
    """
    Possible statuses for a study in a given time.
    """

    CREATED = "created"
    """The study was just created and its initial processing was not done yet."""

    IN_PROGRESS = "in_progress"
    """The study's jobs were created and are currently available for execution."""

    COMPLETED = "completed"
    """All of the study's jobs were executed and it is available for analysis."""

    FAILED = "failed"
    """Some of the study's jobs failed to be executed."""


class StudyRepository:
    """
    Repository class to access studies data.
    Linked to object "UTA01636 Studies > Study List" in ArcGIS Online.
    """

    api: AgolAPI
    table_ref: Table

    def __init__(self):
        self.api = AgolAPI_Injector()
        self.table_ref = self.api.get_table_ref(settings.agol_studies_layer_id)

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

        filters=json.dumps(attributes["filters"] or [])
        del attributes["filters"]
        params=json.dumps(attributes["params"] or [])
        del attributes["params"]

        return Feature(
            attributes=dict(
                **attributes,
                filters=filters,
                params=params
            )
        )

    def get_study(self, study_id: int) -> dict:
        """
        Retrieves a study using its ID.

        Args:
            study_id: The ID of the study to retrieve.

        Returns:
            The retrieved study.
        """
        study = self.api.get_by_id(self.table_ref, study_id)
        return self._feature_to_dict(study)

    def list_studies(self) -> list[dict]:
        """
        Lists all studies.

        Returns:
            The list of all the studies.
        """
        studies = self.table_ref.query(
            where="1=1",
            return_all_records=True,
        )

        return [self._feature_to_dict(f) for f in studies.features]

    def create_study(
        self, filters: list[dict] = [], parameters: list[dict] = []
    ) -> dict:
        """
        Creates a new study.

        Args:
            filters: List of filters for the study.
            parameters: List of parameters for the study.

        Returns:
            The created study.
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

        study_id = result[0]["objectId"]
        return self.get_study(study_id)
