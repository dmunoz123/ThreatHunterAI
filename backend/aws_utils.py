import boto3
import pandas as pd
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class AWSUtils:
    """
    Some basic AWS logic: 
        - s3: upload, download, list, and describe CSV files
    """

    def __init__(self, bucket_name: str = None):
        self.bucket = bucket_name
        if bucket_name:
            self.s3 = boto3.client('s3')
        else:
            self.s3 = None

    def upload_file(self, file_path: Path, key: str, remove_local: bool = True) -> None:
        # Upload local file to S3 and optionally deletes the local copy
        if not self.s3:
            logger.warning("No S3 client configured; skipping upload")
            return

        try:
            self.s3.upload_file(str(file_path), self.bucket, key)
            logger.info("Uploaded %s to s3://%s/%s",
                        file_path, self.bucket, key)
            if remove_local:
                try:
                    os.remove(file_path)
                    logger.info(
                        "Removed local file %s after upload", file_path)
                except OSError:
                    logger.warning("Could not remove local file %s", file_path)
        except Exception:
            logger.exception("Failed to upload %s to S3", file_path)

    def download_file_from_s3(self, key: str, download_path: Path) -> None:
        # Downloads a file from S3 to specified local path.
        if not self.s3:
            logger.warning("No S3 client configured; skipping download")
            return

        try:
            download_path.parent.mkdir(parents=True, exist_ok=True)
            self.s3.download_file(self.bucket, key, str(download_path))
            logger.info("Downloaded s3://%s/%s to %s",
                        self.bucket, key, download_path)
        except Exception:
            logger.exception("Failed to download s3://%s/%s to %s",
                             self.bucket, key, download_path)

    def list_capture_files(self, bucket_name: str, prefix: str):
        resp = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        keys = [o["Key"]
            for o in resp.get("Contents", []) if o["Key"].endswith(".csv")]
        return keys
    
    def load_contents_from_s3obj(self, bucket_name: str, key: str) -> pd.DataFrame:
        body = self.s3.get_object(Bucket=bucket_name, Key=key)["Body"]
        return pd.read_csv(body)


