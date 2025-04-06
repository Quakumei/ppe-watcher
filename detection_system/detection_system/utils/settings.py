import logging
from pathlib import Path
from typing import Mapping, Optional

from pydantic_settings import BaseSettings
from pydantic import BaseModel


class PPEConfig(BaseModel):
    weights_file: Path
    config_file: str = "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"
    score_threshold: float = 0.8
    classes: Mapping[int, str] = {
        0: "Hardhat",
        1: "Mask",
        2: "NO-Hardhat",
        3: "NO-Mask",
        4: "NO-Safety Vest",
        5: "Person",
        6: "Safety Cone",
        7: "Safety Vest",
        8: "machinery",
        9: "vehicle",
    }


class EventDetectorSettings(BaseSettings):
    # logging
    log_level: str = "INFO"

    # pika
    pika_user: str = "guest"
    pika_pass: str = "guest"
    pika_host: str = "localhost"
    pika_routing_key: str = "event_queue"

    # minio
    minio_bucket: str = "ppe-watcher"
    minio_endpoint: str = "s3.remystorage.ru"
    minio_access_key: str = "minio-admin"
    minio_secret_key: str = "minio-secret-password"

    # ppe model
    ppe_config: Optional[PPEConfig] = PPEConfig(
        weights_file="data/models/faster_rcnn_R_101_FPN_apr6.pth"
    )

    @property
    def pika_connection_string(self) -> str:
        return f"amqp://{self.pika_user}:{self.pika_pass}@{self.pika_host}/"

    @property
    def log_level_int(self) -> int:
        levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        return levels[self.log_level.upper()]


def get_settings():
    return EventDetectorSettings()


settings = get_settings()
