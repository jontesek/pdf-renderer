import boto3

from ..clients.s3 import S3Client
from ..settings import S3_BUCKET, S3_CONFIG, S3_DOCUMENTS_PREFIX, ImageSettings, DB_URL
from ..core import Core
from ..processor import Processor
from ..database.base import Database
from ..database.repositories import DocumentRepository

# pylint: disable=invalid-name
core = None


def get_core() -> Core:
    global core
    if not core:
        print("creating core")
        boto_client = boto3.client(
            "s3",
            endpoint_url=S3_CONFIG["endpoint"],
            aws_access_key_id=S3_CONFIG["access_key"],
            aws_secret_access_key=S3_CONFIG["secret_key"],
        )
        s3_client = S3Client(
            client=boto_client, bucket=S3_BUCKET, path_prefix=S3_DOCUMENTS_PREFIX
        )
        db = Database(DB_URL)
        db.create_database()
        repository = DocumentRepository(db.session)
        core = Core(processor=Processor(), document_repository=repository, s3_client=s3_client, image_settings=ImageSettings())
    return core
