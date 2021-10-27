import os
import asyncio
from typing import Any, Dict, Tuple

from fastapi import FastAPI, HTTPException
from uvicorn import Config, Server

from amqp import MQConsumer, MQPublisher
from robot_worker import RobotWorker
from server_services import TaskService
from store import MongoStore, BaseStore


def create_server(
    loop: asyncio.AbstractEventLoop,
    store: BaseStore,
    publisher: MQPublisher,
    collection: str,
) -> Server:
    task_service = TaskService(
        store=store, 
        publisher=publisher, 
        collection=collection
    )

    app = FastAPI()

    @app.post("/tasks", status_code=201)
    async def create_task(data: Dict[str, Any]):
        document, is_created = await task_service.create_task(data)

        if is_created:
            raise HTTPException(409, {"message": document})
        else:
            return {"message": f"task {data} is queued"}

    config = Config(app=app, loop=loop)
    return Server(config)


def create_robot(store: BaseStore, consumer: MQConsumer, collection: str) -> RobotWorker:
    return RobotWorker(store=store, consumer=consumer, collection=collection)


def create_app(loop: asyncio.AbstractEventLoop) -> Tuple[Server, RobotWorker]:
    """ Creating server and robot """
    store = MongoStore(
        connection_uri=os.getenv("MONGO_URI"),
        database=os.getenv("MONGO_DBNAME"),
    )
    publisher = MQPublisher(
        queue_name=os.getenv("QUEUE_NAME"),
        amqp_settings={"url": os.getenv("AMQP_URI")},
        loop=loop,
    )
    consumer = MQConsumer(
        queue_name=publisher.queue_name,
        amqp_settings=publisher.amqp_settings,
        loop=loop
    )
    collection = os.getenv("MONGO_COLLECTION")

    server = create_server(
        loop=loop, 
        store=store, 
        publisher=publisher, 
        collection=collection
    )
    robot = create_robot(store=store, consumer=consumer, collection=collection)

    return server, robot


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    server, robot = create_app(loop)   

    loop.run_until_complete(
        asyncio.gather(server.serve(), robot.start())
    )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(
            asyncio.gather(server.shutdown(), robot.stop())
        )
