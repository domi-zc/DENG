import logging

from google.api_core.exceptions import GoogleAPIError
from google.cloud import storage


class DataLakeWriter:
    """Upload artifacts to a single Google Cloud Storage bucket."""

    logger = logging.getLogger(__name__)

    def __init__(self, bucket_name: str) -> None:
        """Store the target bucket name and prepare a lazy GCS client."""
        if not bucket_name:
            raise ValueError("bucket_name must be a non-empty string")
        self.bucket_name = bucket_name
        self.client: storage.Client | None = None

    def upload_bytes(self, object_path: str, content: bytes) -> str:
        """Upload bytes to the configured bucket and return the resulting gs:// URI."""
        if not object_path:
            raise ValueError("object_path must be a non-empty string")
        if not content:
            raise ValueError("content must not be empty")

        client = self.get_client()
        bucket = client.bucket(self.bucket_name)

        if not bucket.exists():
            raise FileNotFoundError(
                f"GCS bucket {self.bucket_name} does not exist or is not accessible"
            )

        blob = bucket.blob(object_path)

        try:
            blob.upload_from_string(content)
        except GoogleAPIError as error:
            raise RuntimeError(
                f"Failed to upload to gs://{self.bucket_name}/{object_path}: {error}"
            ) from error

        uri = f"gs://{self.bucket_name}/{object_path}"
        self.logger.info(f"Uploaded {len(content)} bytes to {uri}")
        return uri

    def get_client(self) -> storage.Client:
        """Return a cached GCS client, creating it on first use."""
        if self.client is None:
            self.client = storage.Client()
        return self.client
