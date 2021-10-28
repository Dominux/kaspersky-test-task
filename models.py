from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    task_id: Any
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    status: str
