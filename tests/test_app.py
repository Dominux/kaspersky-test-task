import asyncio
from asyncio.base_events import Server
from typing import Tuple

import pytest
import httpx

from main import create_app
from robot_worker import RobotWorker


pytestmark = pytest.mark.asyncio

@pytest.fixture
async def app():
    loop = asyncio.get_event_loop()
    server, robot = create_app(loop, "TEST_")

    # Starting both
    loop.create_task(server.serve())
    await robot.start()

    yield server, robot

    # Stopping both
    await server.shutdown()
    await robot.stop()


async def test_app(app: Tuple[Server, RobotWorker]):
    """
        Integrational test of the whole app logic
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/tasks", 
            json={"lol": {"kek": 12}}, 
        )

    breakpoint()
    print(";p")
    pass
