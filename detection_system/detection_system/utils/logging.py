import logging
from pathlib import Path
from typing import Optional

from .settings import settings

def get_logger(
    name: str,
    filename: Optional[str | Path] = None,
    *,
    verbose=True,
    datefmt="%d.%m.%Y %H:%M:%S",
    log_level=logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)

    if verbose:
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter("[%(name)s] %(asctime)s %(message)s", datefmt=datefmt)
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    if filename:
        file_handler = logging.FileHandler(str(filename))
        file_formatter = logging.Formatter("%(asctime)s %(message)s", datefmt=datefmt)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.setLevel(log_level)
    return logger

logger = get_logger("event_detector", log_level=settings.log_level_int)