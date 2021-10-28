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
        # Trying to connect
        for attempt in range(self.connect_attempts):
            try:
                self.connection = await aio_pika.connect_robust(
                    loop=self.loop, **self.amqp_settings
                )
            except ConnectionError as error:
                if attempt == self.connect_attempts - 1:
                    raise error
                await asyncio.sleep(self.connect_attempt_timeout)

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
