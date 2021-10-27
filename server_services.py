import asyncio
from datetime import datetime
from typing import Any, Dict, Tuple

from store import BaseStore
from amqp import MQPublisher


class TaskService:
    def __init__(self, store: BaseStore, publisher: MQPublisher, collection: str) -> None:
        self._store = store
        self._publisher = publisher
        self._collection = collection

    async def create_task(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
            Main server's logic
        """

        # Emulating data processing
        await asyncio.sleep(1)

        start_time = datetime.now()
        document = dict(task_id=data, start_time=start_time, status="Waiting")
        document, is_created = await self._store.get_or_put(self._collection, document)

        if is_created:
            await self._publisher.publish(data)

        return document, is_created
