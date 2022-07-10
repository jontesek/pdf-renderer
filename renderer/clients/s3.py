from typing import Optional

import botocore


class S3Client:
    def __init__(self, client, bucket: str, path_prefix: str = None) -> None:
        self.client = client
        self.bucket = bucket
        self.path_prefix = path_prefix
        # You can comment this once bucket is created.
        self._check_if_bucket_exists()

    def _check_if_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except botocore.client.ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def save_file(self, key: str, raw_data: bytes) -> str:
        if self.path_prefix:
            key = f"{self.path_prefix}/{key}"
        self.client.put_object(Body=raw_data, Bucket=self.bucket, Key=key)
        return key

    def get_file(self, key: str) -> Optional[bytes]:
        if self.path_prefix:
            key = f"{self.path_prefix}/{key}"
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
        except self.client.exceptions.NoSuchKey as e:
            raise S3FileNotFoundError(key) from e
        return obj["Body"].read()


class S3FileNotFoundError(Exception):
    def __init__(self, key):
        super().__init__(f"file {key} not found")
