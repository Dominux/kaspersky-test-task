import os
import asyncio
from typing import Tuple

from uvicorn import Server

from amqp import MQConsumer, MQPublisher
from robot_worker import RobotWorker
from server import create_server
from store import MongoStore


def get_setting(name: str, prefix: str = ""):
    return os.getenv(f"{prefix}{name}")


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
        collection=collection,
        host=get_setting("HOST", prefix)
    )
    robot = RobotWorker(store=store, consumer=consumer, collection=collection)

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
