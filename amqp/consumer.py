import asyncio
import json
from typing import Any, Callable, Coroutine, Dict, Optional, Union

import aio_pika

from .base import MQBase


class MQConsumer(MQBase):
    def __init__(
        self, 
        amqp_settings: dict, 
        queue_name: str, 
        prefetch_count: Optional[int] = 1,
        loop: Optional[asyncio.BaseEventLoop] = None,
        **queue_declaration: Union[str, Dict[str, Any]]
    ):
        super().__init__(amqp_settings, queue_name, loop)
        self.prefetch_count = prefetch_count

        self.queue_declaration = queue_declaration

        self.handler: Callable
        self.connection: aio_pika.Connection
        self.queue: aio_pika.Queue
        self.channel: aio_pika.Channel

    async def start(self, handle_function: Optional[Callable[[dict], Coroutine]] = None):
        if handle_function:
            self.handler = handle_function
        elif not hasattr(self, 'handler'):
            raise TypeError('handle_function is required to be set at least once')

        await self._attempt_to_connect()

        self.channel = await self.connection.channel()

        await self.channel.set_qos(prefetch_count=self.prefetch_count)
        self.queue = await self.channel.declare_queue(self.queue_name, **self.queue_declaration)
        await self.queue.consume(self._process_message)

    async def stop(self):
        await self.connection.close()
        await self.channel.close()

    async def _process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                message_json = json.loads(message.body.decode("utf-8"))
            except Exception as e:
                print(f'Failed to decode message, got error: {e}')
            else:
                await self.handler(message_json)
    
    