import urllib.parse
from typing import Optional

from pydantic import BaseSettings
import environ
from pydantic.types import SecretStr

env = environ.Env()


class Settings(BaseSettings):
    PROJECT_NAME: Optional[str] = "OC_API_MENTOR"
    SERVER_PORT: Optional[int] = 3000
    DEV: Optional[bool] = False
    MONGO_USER: str = env.str("MONGO_INITDB_ROOT_USERNAME", default="")
    MONGO_PASSWORD: SecretStr = SecretStr(env.str("MONGO_INITDB_ROOT_PASSWORD", default=""))
    MONGO_URL: Optional[str] = "mongodb://{user}:{password}" \
                               "@mongoDB:27017/?authSource=admin".format(user=urllib.parse.quote_plus(MONGO_USER),
                                                                           password=urllib.parse.quote_plus(
                                                                               MONGO_PASSWORD.get_secret_value()))
    MONGO_DB: Optional[str] = "OC"
    MONGO_STUDENT_COLL: Optional[str] = "students"
    MONGO_SESSION_COLL: Optional[str] = "sessions"
    MONGO_INVOICE_COLL: Optional[str] = "invoices"


settings = Settings()
