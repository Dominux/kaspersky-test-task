import os
import asyncio
from typing import Any, Dict, Tuple

from fastapi import FastAPI, HTTPException
from uvicorn import Config, Server

from amqp import MQConsumer, MQPublisher
from robot_worker import RobotWorker
from server_services import TaskService
from store import MongoStore, BaseStore
from models import Task


def get_setting(name: str, prefix: str = ""):
    return os.getenv(f"{prefix}{name}")


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

    @app.on_event("startup")
    async def startup():
        # Starting publisher connection
        await task_service._publisher.start()

    @app.post("/tasks")
    async def create_task(data: Dict[str, Any]):
        document, is_created = await task_service.create_task(data)
        return (
            {"message": f"task {data} is queued"} 
                if is_created 
                else Task(**document).json()
        )

    config = Config(app=app, loop=loop)
    return Server(config)


def create_robot(store: BaseStore, consumer: MQConsumer, collection: str) -> RobotWorker:
    return RobotWorker(store=store, consumer=consumer, collection=collection)


def create_app(
    loop: asyncio.AbstractEventLoop, 
    prefix: str = ""
) -> Tuple[Server, RobotWorker]:
    """ Creating server and robot """
    store = MongoStore(
        connection_uri=get_setting("MONGO_URI", prefix),
        database=get_setting("MONGO_DBNAME", prefix),
    )
    publisher = MQPublisher(
        queue_name=get_setting("QUEUE_NAME", prefix),
        amqp_settings={"url": get_setting("AMQP_URI", prefix)},
        loop=loop,
    )
    consumer = MQConsumer(
        queue_name=publisher.queue_name,
        amqp_settings=publisher.amqp_settings,
        loop=loop
    )
    collection = get_setting("MONGO_COLLECTION", prefix)

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
        loop.run_until_complete(robot.stop())
