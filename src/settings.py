from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    agol_url: str
    agol_client_id: str
    agol_client_secret: str
    agol_config_table_id: str
    agol_project_name: str
    agol_mapviewer_base_url: str
    agol_tabledata_base_url: str
    agol_queue_feature_id: str
    agol_study_area_layer_id: str
    agol_base_layer_id: str
    agol_base_layer_view_id: str
    agol_studies_layer_id: str
    ssurgo_mapunits_layer_id: str
    usa_census_counties_layer_id: str
    prism_base_url: str
    prism_mesh_base_url: str
    prism_mesh_crs: str
    job_manager_id: Optional[int] = None
    job_polling_time: Optional[int] = None
    workdir: str
    daycent_basedir: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
