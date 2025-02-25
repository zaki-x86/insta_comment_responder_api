from fastapi import FastAPI, Request

from app.api import router as api_router
from app.core import get_monitor_state, state
from app.schemas import EventLog

app = FastAPI(
    title="Task API",
    description="API to post to Instagram",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    dependencies=[],
    openapi_tags=[],
)

app.include_router(api_router, tags=[])


@app.on_event("startup")
def on_startup():
    global scheduler
    state.scheduler.start()


@app.middleware("http")
async def record_webhook_notifications(request: Request, call_next):
    monitor = get_monitor_state()
    if request.url.path == "/webhook":
        monitor.append(
            EventLog(
                event="webhook notification",
                data=await request.json(),
            )
        )

    return await call_next(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9999, reload=True)
