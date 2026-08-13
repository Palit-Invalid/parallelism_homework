from pathlib import Path

from src.infrastracture.tasks.app import broker_sync
from src.pdf_reports import generate_event_dashboard_pdf
from src.schemas.base import EventDashboard


@broker_sync.task(
    task_name="generate_event_dashboard_pdf",
    max_retries=2,
    retry_on_error=True,
)
def task_generate_event_dashboard_pdf(dashboard: EventDashboard) -> None:
    generate_event_dashboard_pdf(
        dashboard=dashboard, output_path=Path(__file__).parent.parent.parent.parent / "reports" / "report.pdf"
    )
