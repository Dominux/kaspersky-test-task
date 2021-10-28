from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseStore(ABC):

    @abstractmethod
    async def get_object(self, collection: str, **filters) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def create(self, collection: str, document: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def get_or_create(
        self, 
        collection: str, 
        document: Dict[str, Any],
        **filters: Any
    ) -> Tuple[Dict[str, Any], bool]:
        pass

    @abstractmethod
    async def update(
        self, 
        collection: str, 
        document: Dict[str, Any],
        **filters: Any
    ) -> None:
        pass
