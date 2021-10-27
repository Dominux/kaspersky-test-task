from typing import Any, Dict, Optional, Tuple

import motor.motor_asyncio

from .base_store import BaseStore


class MongoStore(BaseStore):
    def __init__(self, connection_uri: str, database: str) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)
        self.db = self.client[database]

    async def get_object(self, collection: str, **filters) -> Optional[Dict[str, Any]]:
        return await self.db[collection].find_one(filters)

    async def put(self, collection: str, document: Dict[str, Any]) -> Any:
        return await self.db[collection].insert_one(document)

    async def get_or_put(
        self, 
        collection: str, 
        document: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        """
            Trying to get the object, and if it doesn't exist - we create it
        """
        new_document = await self.get_object(collection, task_id=document["task_id"])

        if new_document:
            return new_document, False
        else:
            await self.put(collection, document)
            return document, True
