import os

from pydantic import BaseModel

# Config
S3_CONFIG = {
    "endpoint": os.getenv("S3_ENDPOINT"),
    "access_key": os.getenv("S3_ACCESS_KEY"),
    "secret_key": os.getenv("S3_SECRET_KEY"),
}
S3_BUCKET = os.getenv("S3_BUCKET", "renderer")
REDIS_URL = os.getenv("REDIS_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
DD_HOSTNAME = os.getenv("DD_HOSTNAME")
DD_TRACER_PORT = os.getenv("DD_TRACER_PORT", "8126")
APP_NAME = os.getenv("APP_NAME", "renderer")
ENVIRONMENT = os.getenv("ENVIRONMENT")
DEBUG = os.getenv("DEBUG")
DB_URL = os.getenv("DB_URL")

local = ENVIRONMENT == "local"

# User settings
class ImageSettings(BaseModel):
    dpi: int = 150
    width: int = 1200
    height: int = 1600

S3_DOCUMENTS_PREFIX = "documents"
PDF_FILE_NAME = "input.pdf"