import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream.kafka import KafkaBroker
from granian import Granian
from granian.constants import Interfaces

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.add_event_data import add_event_data_to_db
from src.api.exceptions import setup_exception_handlers
from src.api.routes import main_router
from src.config import config
from src.infrastracture.db.event_view import EventViewCounter
from src.infrastracture.db.manager import DBManager, session_maker
from src.init import redis_manager
from src.services.tickets_purchased_simulation import TicketsPurchasedSimulationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_event_data_to_db()

    async with DBManager(session_maker=session_maker) as db:
        app.state.event_views_counter = EventViewCounter(db, redis_manager)
        await app.state.event_views_counter.start()

        app.state.kafka_broker = KafkaBroker(
            bootstrap_servers=config.KAFKA.BOOTSTRAP_SERVERS,
            linger_ms=50,
        )
        await app.state.kafka_broker.start()

        app.state.tickets_purchased_simulation = TicketsPurchasedSimulationService(
            config=config.KAFKA,
            broker=app.state.kafka_broker,
        )

        await app.state.tickets_purchased_simulation.start()

        yield

        await app.state.event_views_counter.stop()
        await app.state.kafka_broker.stop()
        await app.state.tickets_purchased_simulation.stop()


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
