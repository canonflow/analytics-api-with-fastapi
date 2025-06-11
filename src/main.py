from contextlib import asynccontextmanager

from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db.session import init_db
from api.events import router as event_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before app start up
    init_db()
    yield
    # Clean Up

app = FastAPI(lifespan=lifespan)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(event_router, prefix="/api/events")

# @app.on_event("startup")
# def on_startup():
#     print("Init method for db")

@app.get("/")
def read_root():
    return {"Hello": "Worlder"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}