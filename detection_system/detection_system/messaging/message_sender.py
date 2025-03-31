from abc import ABC, abstractmethod
import asyncio
from typing import Optional

import aio_pika

from ..models.message import Message

class AbstractMessageSender(ABC):
    @abstractmethod
    async def send(message: Message) -> None:
        ...

class PikaMessageSender(AbstractMessageSender):
    def __init__(self, connection_string: str = "amqp://guest:guest@127.0.0.1/", routing_key: str = "event_queue"):
        self.connection_string = connection_string
        self.routing_key = routing_key
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def _init_connection(self) -> None:
        if self.connection is None:
            self.connection = await aio_pika.connect_robust(self.connection_string)

    async def _process_queue(self) -> None:
        await self._init_connection()
        async with self.connection as connection:
            channel = await connection.channel()
            while self._running:
                message_body = await self.queue.get()
                await channel.default_exchange.publish(
                    aio_pika.Message(body=message_body.encode()),
                    routing_key=self.routing_key,
                )
                self.queue.task_done()

    async def start(self) -> None:
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._process_queue())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def send(self, message: Message) -> None:
        serialized: str = message.data.model_dump_json()
        await self.queue.put(serialized)
