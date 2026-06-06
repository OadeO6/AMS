import uuid
from typing import BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from botocore.client import Config

from app.config import settings
from app.exceptions import AppException

# We use standard synchronous boto3 for simple bucket uploads here,
# wrapped in generic exceptions for the API. In a highly loaded API,
# a library like `aioboto3` would be used for full async.

class StorageService:
    def __init__(self) -> None:
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.S3_ENDPOINT_URL,
                config=Config(signature_version="s3v4"),
            )
        else:
            self.s3 = None
            
        self.bucket = settings.S3_BUCKET_NAME

    def upload_file(self, file_obj: BinaryIO, filename: str, content_type: str = "application/octet-stream") -> str:
        """
        Uploads a file to S3 and returns the relative path or URL.
        If S3 is not configured, returns a mock local URL.
        """
        if not self.s3:
            # Fallback for local development if keys aren't set
            unique_filename = f"local-storage/{uuid.uuid4()}-{filename}"
            return f"http://localhost:8000/static/{unique_filename}"

        object_name = f"uploads/{uuid.uuid4()}-{filename}"
        
        try:
            self.s3.upload_fileobj(
                file_obj,
                self.bucket,
                object_name,
                ExtraArgs={"ContentType": content_type}
            )
            # Example representation of an S3 URL
            return f"https://{self.bucket}.s3.amazonaws.com/{object_name}"
        except (BotoCoreError, ClientError) as e:
            raise AppException(status_code=500, detail=f"File upload failed: {str(e)}")

    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """
        Generates a presigned URL to securely download a file.
        """
        if not self.s3:
            return object_name # Just return the mock local path

        try:
            response = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except (BotoCoreError, ClientError) as e:
            raise AppException(status_code=500, detail=f"URL generation failed: {str(e)}")
