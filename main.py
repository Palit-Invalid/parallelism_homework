import asyncio
from typing import Any
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, status

from legacy_client import get_user_todos_sync


class ReportGenerator:
    CACHE_MAP: dict[UUID, dict[str, Any]] = {}

    @classmethod
    def start_generating_report(cls, user_id: int) -> dict:
        task = asyncio.create_task(asyncio.to_thread(get_user_todos_sync, user_id))
        uuid = uuid4()
        result = {"job_id": uuid, "status": "running"}
        cls.CACHE_MAP[uuid] = {"task": task, "result": result}
        return result

    @classmethod
    def get_report_by_id(cls, job_id: UUID) -> dict[str, Any] | None:
        job = cls.CACHE_MAP.get(job_id)
        if job is None:
            return None

        task: asyncio.Task = job["task"]

        try:
            report = task.result()
        except asyncio.CancelledError:
            result = {"job_id": job_id, "status": "error"}
            cls.CACHE_MAP[job_id]["result"] = result
            return result
        except asyncio.InvalidStateError:
            result = {"job_id": job_id, "status": "running"}
            cls.CACHE_MAP[job_id]["result"] = result
            return result

        result = {"job_id": job_id, "status": "done", "result": report}
        cls.CACHE_MAP[job_id]["result"] = result
        return result


app = FastAPI()


@app.post("/reports/<user_id>")
async def generate_report(user_id: int):
    return ReportGenerator.start_generating_report(user_id)


@app.get("/reports/job/<job_id>")
async def get_report(job_id: UUID):
    report = ReportGenerator.get_report_by_id(job_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    return report


@app.get("/ping")
async def ping():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", loop="uvloop")
