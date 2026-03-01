import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class StorageService:
    """
    Handles interactions with MinIO/S3 Object Storage.
    Includes retry logic and bucket initialization.
    """
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_REPORTS
        self.secure = settings.MINIO_SECURE
        
        # Initialize Boto3 Client
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.secure,
                # Config for local MinIO (often needed to avoid DNS issues with bucket names)
                config=boto3.session.Config(signature_version='s3v4') 
            )
            logger.info(f"[Storage] Initialized MinIO client at {self.endpoint}")
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"[Storage] Failed to initialize client: {e}")
            self.s3_client = None

    def _ensure_bucket_exists(self):
        """Creates the bucket if it doesn't exist."""
        if not self.s3_client:
            return

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"[Storage] Bucket '{self.bucket_name}' exists.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"[Storage] Created bucket '{self.bucket_name}'.")
                    
                    # Set a basic public read policy if needed (or keep private)
                    # For now, we keep it private by default.
                except Exception as create_err:
                    logger.error(f"[Storage] Failed to create bucket: {create_err}")
            else:
                logger.error(f"[Storage] Error checking bucket: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def upload_file(self, file_content: str, filename: str, metadata: dict = None) -> str:
        """
        Uploads a string content as a file to MinIO.
        Returns the object URL or Key.
        """
        if not self.s3_client:
            logger.warning("[Storage] S3 Client not available. Skipping upload.")
            return None

        try:
            # Convert string to bytes stream
            file_stream = io.BytesIO(file_content.encode('utf-8'))
            
            extra_args = {
                'ContentType': 'text/markdown',
                'Metadata': metadata or {}
            }

            self.s3_client.upload_fileobj(
                file_stream,
                self.bucket_name,
                filename,
                ExtraArgs=extra_args
            )
            
            logger.info(f"[Storage] Successfully uploaded {filename} to {self.bucket_name}")
            return f"{self.bucket_name}/{filename}"
            
        except Exception as e:
            logger.error(f"[Storage] Upload failed for {filename}: {e}")
            raise e # Retry will catch this

# Global Instance
storage = StorageService()
