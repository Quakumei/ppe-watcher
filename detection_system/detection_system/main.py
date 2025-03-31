import asyncio

from .core.event_detector import FakeEventDetector
from .utils.logging import logger


async def main():
    ed = FakeEventDetector()
    await ed.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received Ctrl-C")