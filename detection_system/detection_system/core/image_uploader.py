import io
import numpy as np
import cv2

from minio import Minio
from minio.error import S3Error

from ..utils.settings import settings


class ImageUploader:
    def __init__(self, client: Minio, bucket_name: str) -> None:
        self._client = client
        self._bucket = bucket_name

    async def _upload_image(self, image: np.ndarray, tag: str) -> str:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

        buffer = cv2.imencode(".jpg", image)[1].tobytes()
        image_stream = io.BytesIO(buffer)
        object_name = f"{tag}"

        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=image_stream,
            length=len(buffer),
            content_type="image/jpeg",
        )

        return self._client.get_presigned_url("GET", self._bucket, object_name)


def get_minio_client(
    endpoint: str, access_key: str, secret_key: str, secure: bool = True
) -> Minio:
    return Minio(
        endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=secure
    )


image_uploader = ImageUploader(
    get_minio_client(
        settings.minio_endpoint,
        settings.minio_access_key,
        settings.minio_secret_key,
    ),
    bucket_name=settings.minio_bucket,
)
