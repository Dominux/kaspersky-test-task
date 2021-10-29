from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
from typing import Optional

import aio_pika


class MQBase(ABC):
    def __init__(
        self, 
        amqp_settings: dict, 
        queue_name: str, 
        loop: Optional[asyncio.BaseEventLoop] = None,
        connect_attempts: int = 3,
        connect_attempt_timeout: int = 10,
    ):
        self.amqp_settings = amqp_settings
        self.loop = loop or asyncio.get_event_loop()
        self.queue_name = queue_name
        self.connect_attempts = connect_attempts
        self.connect_attempt_timeout = connect_attempt_timeout

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    async def _attempt_to_connect(self):
        """ Trying to connect """
        for attempt in range(self.connect_attempts):
            try:
                self.connection = await aio_pika.connect_robust(
                    loop=self.loop, **self.amqp_settings
                )
            except ConnectionError as error:
                if attempt == self.connect_attempts - 1:
                    raise error
                await asyncio.sleep(self.connect_attempt_timeout)

