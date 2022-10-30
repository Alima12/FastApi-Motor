from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = ""

    email_regex: str = "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    username_regex: str = "^[a-zA-Z0-9][\w]{2,}[a-zA-Z0-9]$"

    authjwt_secret_key: str = "hi"
    authjwt_access_token_expires: int = 800
    authjwt_refresh_token_expires: int = 900
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
