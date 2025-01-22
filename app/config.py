# is used to check and validate environment variables
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    # NO NEED TO CHANGE TO AN INT CAUSE IT WILL STILL BE SENT TO THE SQLALCHEMY URL
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expiration_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
print(settings.database_hostname)
print(type(settings.access_token_expiration_minutes))
