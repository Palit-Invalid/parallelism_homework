import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from granian import Granian
from granian.constants import Interfaces

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.add_event_data import add_event_data_to_db
from src.api.exceptions import setup_exception_handlers
from src.api.routes import main_router
from src.infrastracture.db.event_view import EventViewCounter
from src.infrastracture.db.manager import DBManager, session_maker
from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_event_data_to_db()

    async with DBManager(session_maker=session_maker) as db:
        app.state.event_views_counter = EventViewCounter(db, redis_manager)
        await app.state.event_views_counter.start()

        yield

        await app.state.event_views_counter.stop()


app = FastAPI(
    title="API Афиши",
    lifespan=lifespan,
    swagger_ui_parameters={"displayRequestDuration": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(main_router)


if __name__ == "__main__":
    Granian(target="src.main:app", reload=True, interface=Interfaces.ASGI).serve()
