from pathlib import Path

from src.infrastracture.tasks.app import broker_sync, broker_async
from src.pdf_reports import generate_event_dashboard_pdf
from src.schemas.base import EventDashboard
from src.infrastracture.db.manager import DBManager, session_maker
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
        await BookingService(db=db).delete_overdue_bookings()
