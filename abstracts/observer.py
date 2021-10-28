from abc import ABC, abstractmethod
from typing import List



class AbstractObserver(ABC):

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class AbstractObservable(ABC):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._observers: List[AbstractObserver] = []

    def subsribe(self, subsruber: AbstractObserver) -> None:
        self._observers.append(subsruber)

    def unsubsribe(self, subsruber: AbstractObserver) -> None:
        self._observers.remove(subsruber)

    def unsubsribe_all(self) -> None:
        for observer in self._observers:
            self.unsubsribe(observer)

    def notify(self, *args, **kwargs) -> None:
        for observer in self._observers:
            observer.update(*args, **kwargs)
