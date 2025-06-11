from typing import List, Optional
from pydantic import BaseModel, Field

"""
id
page
description
"""

class EventSchema(BaseModel):
    id: int
    page: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="My Description")

class EventCreateSchema(BaseModel):
    page: str
    description: Optional[str] = ""

class EventUpdateSchema(BaseModel):
    description: str
    page: Optional[str] = ""

class EventListSchema(BaseModel):
    results: List[EventSchema]
    count: int