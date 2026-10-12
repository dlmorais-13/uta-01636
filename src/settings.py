from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    The list of the settings available for the app.
    """

    debug: Optional[bool] = False
    """
    If True, enabled a debugging mode in the system, which is more verbose.
    """

    agol_url: str
    """Base URL for ArcGIS Online access."""

    agol_api_key: str
    """The API Key to authenticate to ArcGIS Online."""

    agol_client_id: str
    """The cliend ID to authenticate with ArcGIS Online."""

    agol_client_secret: str
    """The cliend secret to authenticate with ArcGIS Online."""

    # agol_default_crs: str
    # """The default CRS of the objects saved to ArcGIS Online."""

    agol_config_table_id: str
    """The ID for the configuration table in ArcGIS Online."""

    # agol_project_name: str
    # """The project name in ArcGIS Online."""

    # agol_mapviewer_base_url: str
    # agol_tabledata_base_url: str

    agol_queue_feature_id: str
    """The ID for the job queue in ArcGIS Online."""

    agol_study_area_layer_id: str
    """The ID for the study area layer in ArcGIS Online."""

    agol_base_layer_id: str
    """The ID for the base layer in ArcGIS Online."""

    agol_base_layer_view_id: str
    """The ID for the base layer public view in ArcGIS Online."""

    agol_simulations_layer_id: str
    """The ID for the simulations layer in ArcGIS Online."""

    agol_simulations_layer_view_id: str
    """The ID for the public view of the simulations in ArcGIS Online."""

    ssurgo_mapunits_layer_id: str
    """The ID for SSURGO layer of map units in ArcGIS Online."""

    usa_census_counties_layer_id: str
    """The ID for USA Census counties in ArcGIS Online."""

    daymet_base_url: str
    """The base URL to access DayMet API."""

    prism_api_url: str
    """The base URL to access Prism API."""

    # prism_base_url: str
    # prism_nacse_url: str
    # prism_mesh_base_url: str
    # prism_mesh_crs: str

    job_manager_id: Optional[int] = None
    """
    The ID for the job manager to use in this instance of the app.
    If the defined, the instance will behave as a job executor instead
    of a webapi.
    """

    job_polling_time: Optional[int] = None
    """The time between checks for jobs to be executed (in seconds)."""

    workdir: str
    """The workdir to use for job executions and caching."""

    daycent_basedir: str
    """The directory with DayCent template files."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
