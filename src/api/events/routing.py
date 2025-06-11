import os
from sched import Event

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from timescaledb.hyperfunctions import time_bucket
from typing import List

from .models import (
    EventModel,
    EventBucketSchema,
    EventCreateSchema,
    get_utc_now
)
from sqlalchemy import func, case
from datetime import datetime, timedelta, timezone

from ..db.session import get_session

router = APIRouter()

DEFAULT_LOOKUP_PAGES = [
    "/", "/about", "/pricing", "/contact",
    "/blog", "/products", "/login", "/signup",
    "/dashboard", "/settings"
]

# GET /api/events
@router.get("/", response_model=List[EventBucketSchema])
def read_events(
        duration: str = Query(default='1 day'),
        pages: List = Query(default=None),
        session: Session = Depends(get_session)
    ):

    # query = select(EventModel).order_by(EventModel.updated_at.desc()).limit(10)
    os_case = case(
        (EventModel.user_agent.ilike('%windows%'), 'Windows'),
        (EventModel.user_agent.ilike('%macintosh%'), 'MacOS'),
        (EventModel.user_agent.ilike('%iphone%'), 'iOS'),
        (EventModel.user_agent.ilike('%android%'), 'Android'),
        (EventModel.user_agent.ilike('%linux%'), 'Linux'),
        else_='Other'
    ).label("operating_system")

    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES

    query = (
        select(
            bucket.label("bucket"),
            os_case,
            EventModel.page.label('page'),
            func.avg(EventModel.duration).label('avg_duration'),
            func.count().label("count")
        )
        .where(
            EventModel.page.in_(lookup_pages)
        )
        .group_by(
            bucket,
            os_case,
            EventModel.page
        )
        .order_by(
            bucket,
            os_case,
            EventModel.page
        )
    )
    results = session.exec(query).fetchall()

    return results

# POST /api/events
@router.post("/", response_model=EventModel)
def create_event(
        payload: EventCreateSchema,
        session: Session = Depends(get_session)
    ):
    print(payload)
    data = payload.model_dump() # payload -> dict -> pydantic

    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj) # Get created object with ID
    return obj


# GET /api/events/<event_id>
@router.get("/{event_id}", response_model=EventModel)
def get_event(
        event_id: int,
        session: Session = Depends(get_session)
    ):
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    return result

# PUT /api/events/<event_id>
# @router.put("/{event_id}", response_model=EventModel)
# def update_event(
#         event_id: int,
#         payload: EventUpdateSchema,
#         session: Session = Depends(get_session)
#     ):
#     query = select(EventModel).where(EventModel.id == event_id)
#     obj = session.exec(query).first()
#
#     if not obj:
#         raise HTTPException(
#             status_code=404,
#             detail="Event not found"
#         )
#
#     data = payload.model_dump()  # payload -> dict -> pydantic
#     for key, val in data.items():
#         if key == "id":
#             continue
#         setattr(obj, key, val)
#
#     obj.updated_at = get_utc_now()
#     session.add(obj)
#     session.commit()
#     session.refresh(obj)
#     return obj

# DELETE /api/events/<event_id>
# @router.delete("/{event_id}", response_model=EventModel)
# def get_event(event_id: str):
#     return {
#         "id": event_id
#     }