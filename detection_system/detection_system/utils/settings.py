import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # logging
    log_level: str = "INFO"

    # pika
    pika_user: str = "guest"
    pika_pass: str = "guest"
    pika_host: str = "localhost"
    pika_routing_key: str = "event_queue"

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
    return Settings()

settings = get_settings()