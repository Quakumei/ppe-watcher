import asyncio
from pathlib import Path

from .core.demo_event_detector import SimpleVideoEventDetector as EventDetector
from .utils.logging import logger


async def main():
    # sample_video_path = Path("data/cam_videos/1.mp4")
    sample_rtsp_stream = "rtsp://localhost:8554/cam"
    ed = EventDetector(sample_rtsp_stream)
    await ed.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received Ctrl-C")
