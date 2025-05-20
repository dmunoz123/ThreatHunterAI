import boto3
import pandas as pd


def list_capture_files(bucket_name: str, prefix: str):
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    keys = [o["Key"]
            for o in resp.get("Contents", []) if o["Key"].endswith(".csv")]
    return keys


def load_csv_from_s3(bucket_name: str, key: str) -> pd.DataFrame:
    s3 = boto3.client("s3")
    body = s3.get_object(Bucket=bucket_name, Key=key)["Body"]
    return pd.read_csv(body)
