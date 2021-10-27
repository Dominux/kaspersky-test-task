from typing import Any, Dict

import motor.motor_asyncio

from .base_store import BaseStore


class MongoStore(BaseStore):
    def __init__(self, connection_uri: str, database: str) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)
        self.db = self.client[database]

    async def put(self, collection: str, document: Dict[str, Any]) -> Any:
        return await self.db[collection].insert_one(document)
