from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
from typing import Optional


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
