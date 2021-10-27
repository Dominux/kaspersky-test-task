import asyncio
from datetime import datetime
from typing import Any, Dict

from store import BaseStore
from amqp import MQPublisher


class TaskService:
    def __init__(self, store: BaseStore, publisher: MQPublisher, collection: str) -> None:
        self._store = store
        self._publisher = publisher
        self._collection = collection

    async def create_task(self, data: Dict[str, Any]) -> None:
        """
            Main logic of server
        """
        await asyncio.sleep(1)
        start_time = datetime.now()
        document = dict(**data, start_time=start_time, status="Waiting")
        await self._store.put(self._collection, document)
        await self._publisher.publish(data)
