from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    agol_url: str
    agol_client_id: str
    agol_client_secret: str
    agol_project_folder: str
    agol_config_table_id: str
    agol_project_group_id: str
    agol_default_crs: str
    agol_project_name: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
