from datetime import datetime, timezone
from operator import index
from typing import List, Optional

import sqlmodel
from sqlmodel import SQLModel, Field
from timescaledb import TimescaleModel

def get_utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=timezone.utc)

class EventModel(TimescaleModel, table=True):
    page: str = Field(index=True) # /about, /contact, etc.
    user_agent: Optional[str] = Field(default="", index=True) # Browser
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True) # From Google or its own website
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)

    __chunk_time_interval__ = "INTERVAL 1 day"
    __drop_after__ = "INTERVAL 3 months"

class EventCreateSchema(TimescaleModel):
    page: str
    user_agent: Optional[str] = Field(default="", index=True)  # Browser
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)  # From Google or its own website
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)

class EventListSchema(TimescaleModel):
    results: List[EventModel]
    count: int

class EventBucketSchema(TimescaleModel):
    bucket: datetime
    page: str
    ua: Optional[str] = ""
    operating_system: Optional[str] = ""
    avg_duration: Optional[float] = 0.0
    count: int