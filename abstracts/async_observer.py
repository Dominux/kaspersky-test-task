import asyncio
from abc import ABCMeta

from abstracts import AbstractObservable, AbstractObserver


class AsyncAbstractObserver(AbstractObserver, metaclass=ABCMeta):
	async def update(self, *args, **kwargs):
		raise NotImplementedError


class AsyncAbstractObservable(AbstractObservable, metaclass=ABCMeta):
	async def notify(self, *args, **kwargs):
		await asyncio.gather(*[
			observer.update(*args, **kwargs) for observer in self._observers
		])
