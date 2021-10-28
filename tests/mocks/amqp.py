from typing import Any, Callable, Coroutine, Dict, List, NewType, Optional

from abstracts import AsyncAbstractObserver, AsyncAbstractObservable


MessageType = NewType('Message', Dict[str, Any])


class QueueMock(AsyncAbstractObservable, AsyncAbstractObserver):
    """
        Mock AMQP Queue (for basical using only!)
    """
    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.name = name
        self.messages: List[MessageType] = [] 

    async def update(self, message=MessageType, *args, **kwargs):
        if self._observers:
            await self.notify(message)
        else:
            self.messages.append(message)

    async def subscribe(self, subsriber: AsyncAbstractObservable) -> None:
        super().subsribe(subsriber)

        # Synchronical cycle of messages publishing
        # to publish them one by one in the original order
        for message in self.messages:
            await self.notify(message)


class MQPublisherMock(AsyncAbstractObservable):
    """
        Mock MQPublisher
    """

    def __init__(self, queue: QueueMock, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = queue
        self.queue_name = queue.name
    
    async def start(self):
        self.subsribe(self.queue)

    async def stop(self):
        self.unsubsribe_all()

    async def publish(self, message: MessageType):
        await self.notify(message)


class MQConsumerMock(AsyncAbstractObserver):
    """
        Mock MQConsumer
    """

    def __init__(self, queue: QueueMock, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = queue
        self.queue_name = queue
    
    async def start(self, handle_function: Optional[Callable[[dict], Coroutine]]):
        if handle_function:
            self.handler = handle_function
        elif not hasattr(self, 'handler'):
            raise TypeError('handle_function is required to be set at least once')

        await self.queue.subscribe(self)

    async def stop(self):
        self.queue.unsubscribe(self)

    async def update(self, message: MessageType, *args, **kwargs):
        await self.handler(message)

