"""Fetch data from Google Cloud Storage and load it into memory."""

import io
import logging

import pandas as pd
from google.cloud import storage


class GCSFetcher:
    """Download objects from GCS and parse CSV content into DataFrames."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Prepare a lazy GCS client."""
        self.client: storage.Client | None = None

    def download_csv(self, bucket_name: str, object_path: str) -> bytes:
        """Download an object from GCS and return its bytes."""
        if not bucket_name:
            raise ValueError("bucket_name must be a non-empty string")
        if not object_path:
            raise ValueError("object_path must be a non-empty string")

        client = self.get_client()
        blob = client.bucket(bucket_name).blob(object_path)

        if not blob.exists(client):
            raise FileNotFoundError(f"gs://{bucket_name}/{object_path} does not exist")

        content = blob.download_as_bytes()

        self.logger.info(f"Downloaded gs://{bucket_name}/{object_path} ({len(content)} bytes)")
        return content

    def load_dataframe(self, csv_bytes: bytes) -> pd.DataFrame:
        """Parse CSV bytes into a pandas DataFrame."""
        if not csv_bytes:
            raise ValueError("csv_bytes must not be empty")

        df = pd.read_csv(io.BytesIO(csv_bytes))
        if df.empty:
            raise ValueError("Parsed DataFrame is empty")

        self.logger.info(f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df

    def get_client(self) -> storage.Client:
        """Return a cached GCS client, creating it on first use."""
        if self.client is None:
            self.client = storage.Client()
        return self.client
