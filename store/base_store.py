from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class BaseStore(ABC):

    @abstractmethod
    async def get_object(self, collection: str, **filters) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def put(self, collection: str, document: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def get_or_put(
        self, 
        collection: str, 
        document: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        pass
