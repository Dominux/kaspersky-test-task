import asyncio
from typing import Any, Dict, Tuple

import pytest
from uvicorn import Server
import httpx

from main import create_app
from robot_worker import RobotWorker
from models import Task
from tests import mocks


pytestmark = pytest.mark.asyncio

DATA = {"test_data": {"kek": 12}}
ANOTHER_DATA = {"lol": "test_string"}
PROCESSING_TIME = .01
COLLECTION = "test"
QUEUE_NAME = "Q_Test"


@pytest.fixture
async def app():

    loop = asyncio.get_event_loop()

    # Creating mocks
    store_mock = mocks.StoreMock(COLLECTION)

    queue = mocks.QueueMock(QUEUE_NAME)
    publisher_mock = mocks.MQPublisherMock(queue)
    consumer_mock = mocks.MQConsumerMock(queue)

    # Mocks injecting 
    server, robot = create_app(
        loop=loop, 
        prefix="TEST_",
        store=store_mock,
        publisher=publisher_mock,
        consumer=consumer_mock,
        collection=COLLECTION,
        server_processig_time=PROCESSING_TIME
    )

    # Setting custom robot processing time
    robot.proccesing_time = PROCESSING_TIME

    # Starting both
    loop.create_task(server.serve())

    await robot.start()

    yield server, robot


async def test_app(app: Tuple[Server, RobotWorker]):
    """
        Integrational test of the whole app logic
    """

    _, robot = app

    # Making the first request
    task = await _test_creating(DATA, robot)

    # Making the second request with the same data
    response = await _make_post_request(DATA)

    assert response.is_success
    assert Task.parse_obj(response.json()["message"]) == Task(**task)
    
    # Making another request with another data
    await _test_creating(ANOTHER_DATA, robot)


async def _test_creating(data: Any, robot: RobotWorker) -> Dict[str, Any]:
    response = await _make_post_request(data)

    assert response.is_success
    assert response.json()["message"] == f"task {data} is queued"

    # Waiting for robot processing and retreiving the object from database
    await asyncio.sleep(PROCESSING_TIME)
    task = await robot._store.get_object(
        robot._collection, task_id=DATA
    )

    assert task["task_id"] == DATA
    assert task["status"] == "Done"

    return task


async def _make_post_request(data: Any) -> httpx.Response:
    async with httpx.AsyncClient(timeout=None) as client:
        return await client.post(
            "http://localhost:8000/tasks", 
            json=data,
        )

