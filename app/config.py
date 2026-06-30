from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_url: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()