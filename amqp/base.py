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
    ):
        self.amqp_settings = amqp_settings
        self.loop = loop or asyncio.get_event_loop()
        self.queue_name = queue_name

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
