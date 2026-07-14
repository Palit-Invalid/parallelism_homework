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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_event_data_to_db()
    yield


app = FastAPI(title="API Афиши", lifespan=lifespan)

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
