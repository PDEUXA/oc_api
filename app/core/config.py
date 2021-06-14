from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: Optional[str] = "OC_API_MENTOR"
    SERVER_PORT: Optional[int] = 3000
    DEV: Optional[bool] = False

    MONGO_URL: Optional[str] = "mongodb://localhost:27017"
    MONGO_DB: Optional[str] = "OC"
    MONGO_STUDENT_COLL: Optional[str] = "students"
    MONGO_SESSION_COLL: Optional[str] = "sessions"
    MONGO_INVOICE_COLL: Optional[str] = "invoices"


settings = Settings()
