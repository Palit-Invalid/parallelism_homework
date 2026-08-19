from pathlib import Path


from src.config import config
from src.infrastracture.api_connectors.protection import ProtectionConnector
from src.infrastracture.db.manager import DBManager, session_maker
from src.infrastracture.tasks.app import broker_async, broker_sync
from src.pdf_reports import generate_event_dashboard_pdf
from src.schemas.base import EventDashboard
from src.services.booking import BookingService


@broker_sync.task(
    task_name="generate_event_dashboard_pdf",
    max_retries=2,
    retry_on_error=True,
)
def task_generate_event_dashboard_pdf(dashboard: EventDashboard) -> None:
    generate_event_dashboard_pdf(
        dashboard=dashboard, output_path=Path(__file__).parent.parent.parent.parent / "reports" / "report.pdf"
    )


@broker_async.task(
    task_name="delete_overdue_bookings",
    schedule=[
        {
            "schedule_id": "delete_overdue_bookings-every-minute",
            "cron": "* * * * *",
        }
    ],
)
async def delete_overdue_bookings():
    async with DBManager(session_maker=session_maker) as db:
        await BookingService(
            db=db,
            protection_connector=ProtectionConnector(base_url=config.PROTECTION.url),
        ).delete_overdue_bookings()


@broker_async.task(
    task_name="get_protection_after_fail",
)
async def get_protection_after_fail(booking_id: int, ticket_amount: int, event_category: str):
    async with DBManager(session_maker=session_maker) as db:
        await BookingService(
            db=db,
            protection_connector=ProtectionConnector(base_url=config.PROTECTION.url),
        ).add_protection(booking_id=booking_id, ticket_amount=ticket_amount, event_category=event_category)
