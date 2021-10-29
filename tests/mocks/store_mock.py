from typing import Any, Dict, List, Optional, Tuple
from store import BaseStore


class StoreMock(BaseStore):
    """
        Store Mock
    """
    def __init__(self, *collections: str) -> None:
        self._store: Dict[str, List[str, Any]] = {collection: [] for collection in collections}

    async def get_object(
        self, 
        collection: str, 
        **filters
    ) -> Optional[Dict[str, Any]]:
        for doc in self._store[collection]:
            if all(doc[k] == v for k, v in filters.items()):
                return doc

    async def create(self, collection: str, document: Dict[str, Any]) -> Any:
        self._store[collection].append(document)

    async def get_or_create(
        self, 
        collection: str, 
        document: Dict[str, Any],
        **filters: Any
    ) -> Tuple[Dict[str, Any], bool]:
        existed = await self.get_object(collection, **filters)

        if existed:
            return existed, False
        else:
            await self.create(collection, document)
            return document, True

    async def update(
        self, 
        collection: str, 
        document: Dict[str, Any], 
        **filters: Any
    ) -> None:
        for i, doc in enumerate(self._store[collection]):
            if all(doc[k] == v for k, v in filters.items()):
                self._store[collection][i].update(**document)
