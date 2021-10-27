import asyncio
from datetime import datetime

from amqp import MQConsumer
from store import BaseStore


class RobotWorker:
    def __init__(self, store: BaseStore, consumer: MQConsumer, collection: str) -> None:
        self._consumer = consumer
        self._store = store
        self._collection = collection

    async def start(self):
        await self._consumer.start(self.handle)

    async def stop(self):
        await self._consumer.stop()

    async def handle(self, message: dict):
        """
            Main logic of robot
        """
        await asyncio.sleep(1)
        finish_time = datetime.now()
        document = {
            "task_id": message,
            "finish_time": finish_time,
            "status": "Done",
        }
        await self._store.put(
            collection=self._collection, 
            document=document
        )
