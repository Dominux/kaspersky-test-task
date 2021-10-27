from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStore(ABC):
    
    @abstractmethod
    async def put(self, collection: str, document: Dict[str, Any]) -> Any:
        pass
