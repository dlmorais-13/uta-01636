from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    agol_url: str
    agol_client_id: str
    agol_client_secret: str
    # agol_project_folder: str
    agol_config_table_id: str
    # agol_project_group_id: str
    agol_default_crs: str
    agol_project_name: str
    agol_mapviewer_base_url: str
    agol_tabledata_base_url: str
    agol_queue_feature_id: str
    agol_study_area_layer_id: str
    job_manager_id: int
    job_manager_count: int
    job_polling_time: int
    workdir: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
