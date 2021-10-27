import asyncio
import json
from typing import Optional

import aio_pika

from .base import MQBase


class MQPublisher(MQBase):
    def __init__(
        self, 
        amqp_settings: dict, 
        queue_name: str,
        loop: Optional[asyncio.BaseEventLoop] = None,
    ):
        super().__init__(amqp_settings, queue_name, loop)

        self.connection: aio_pika.Connection

    async def start(self):
        self.connection = await aio_pika.connect_robust(
            **self.amqp_settings, url=None, loop=self.loop
        )

    async def stop(self):
        await self.connection.close()

    async def publish(self, message: dict):
        message = json.dumps(message).encode("utf-8")

        async with self.connection.channel() as channel:
            result = await channel.default_exchange.publish(
                aio_pika.Message(message),
                routing_key=self.queue_name,
            )

        return result
