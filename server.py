import asyncio
import json
import numbers
from datetime import datetime
from typing import Any, Dict, Tuple

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from uvicorn import Config, Server

from store import BaseStore
from amqp import MQPublisher
from models import Task


class TaskService:
    def __init__(
        self, 
        store: BaseStore, 
        publisher: MQPublisher, 
        collection: str,
        processing_time: numbers.Number
    ) -> None:
        self._store = store
        self._publisher = publisher
        self._collection = collection
        self._procesing_time = processing_time

    async def create_task(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """
            Main server's logic
        """

        # Check whether document already exists
        if document := await self._store.get_object(self._collection, task_id=data):
            return document, False

        # Emulating data processing
        await asyncio.sleep(self._procesing_time)

        # Creating document, storing it and publishing data to the robot
        start_time = datetime.now()
        document = dict(task_id=data, start_time=start_time, status="Waiting")
        await self._store.create(self._collection, document)
        await self._publisher.publish(data)

        return document, True


def create_server(
    loop: asyncio.AbstractEventLoop,
    store: BaseStore,
    publisher: MQPublisher,
    collection: str,
    host: str,
    processing_time: numbers.Number
) -> Server:
    task_service = TaskService(
        store=store, 
        publisher=publisher, 
        collection=collection,
        processing_time=processing_time
    )

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        # Starting publisher connection
        await task_service._publisher.start()

    @app.get("/tasks")
    async def task_form():
        """ Getting tasks html form """
        with open("templates/tasks/form.html", "r") as f:
            return HTMLResponse(f.read())

    @app.post("/tasks", status_code=201)
    async def create_task(data: Dict[str, Any]):
        document, is_created = await task_service.create_task(data)

        if is_created:
            return {"message": f"task {data} is queued"} 
        else:
            return JSONResponse(
                status_code=200, 
                content={"message": json.loads(Task(**document).json())}
            )

    config = Config(app=app, loop=loop, host=host)
    return Server(config)
