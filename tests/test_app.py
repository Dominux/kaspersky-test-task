import time
import asyncio
from typing import Any, Dict, Tuple

import pytest
from uvicorn import Server
import httpx

from main import create_app
from robot_worker import RobotWorker
from models import Task


pytestmark = pytest.mark.asyncio

DATA = {"test_data": {"kek": 12}}
ANOTHER_DATA = {"lol": "test_string"}


@pytest.fixture
async def app():
    loop = asyncio.get_event_loop()
    server, robot = create_app(loop, "TEST_")

    # Truncating collection
    await robot._store._db[robot._collection].delete_many({})

    # Starting both
    loop.create_task(server.serve())

    await robot.start()

    yield server, robot

    # Stopping robot
    await robot.stop()


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
    assert Task.parse_raw(response.json()) == Task(**task)
    
    # Making another request with another data
    await _test_creating(ANOTHER_DATA, robot)


async def _test_creating(data: Any, robot: RobotWorker) -> Dict[str, Any]:
    response = await _make_post_request(data)

    assert response.is_success
    assert response.json()["message"] == f"task {data} is queued"

    # Waiting for robot processing and retreiving the object from database
    await asyncio.sleep(3)
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

