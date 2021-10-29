from typing import Any, Dict, List, Optional, Tuple

import motor.motor_asyncio

from .base_store import BaseStore


class MongoStore(BaseStore):
    def __init__(self, connection_uri: str, database: str) -> None:
        self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)
        self._db = self._client[database]

    async def get_object(self, collection: str, **filters) -> Optional[Dict[str, Any]]:
        return await self._db[collection].find_one(filters)

    async def create(self, collection: str, document: Dict[str, Any]) -> Any:
        return await self._db[collection].insert_one(document)

    async def update(
        self, 
        collection: str, 
        document: Dict[str, Any],
        **filters: Any
    ) -> None:
        document_setter = {"$set": document}
        await self._db[collection].update_one(filters, document_setter)
    