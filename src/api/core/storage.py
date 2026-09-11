import boto3
from botocore.client import Config
from api.core.config import AWS_ENDPOINT_URL_S3, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

s3_client = boto3.client(
    's3',
    endpoint_url=AWS_ENDPOINT_URL_S3,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
    config=Config(signature_version='s3v4')
)
