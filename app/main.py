import os
from typing import Optional
from datetime import datetime
from decouple import config
from fastapi import FastAPI, Request
from starlette.responses import FileResponse

from app.schemas import Message, EventLog
from app.service import FBBService
from apscheduler.schedulers.background import BackgroundScheduler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="Task API",
    description="API to post to Instagram",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

scheduler = BackgroundScheduler()

fbb = FBBService(
    access_token=config("META_DEVELOPER_ACCESS_TOKEN"),
    insta_account=config("INSTAGRAM_ACCOUNT_ID"),
)

monitor: list[EventLog] = []


def reset_monitor():
    global monitor
    monitor = []


scheduler.add_job(reset_monitor, "interval", minutes=15)


@app.on_event("startup")
def on_startup():
    global scheduler
    scheduler.start()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/monitor")
async def get_monitor() -> list[EventLog]:
    return monitor


@app.post("/post")
def post_message_to_instagram_account(message: Message) -> dict[str, Optional[str]]:
    """Sends a post to instagram"""
    id = fbb.send_post(message.message, message.image_url)

    if id:
        return {"post_id": id}
    return {"post_id": None}


@app.get("/webhook")
async def verify_webhook(request: Request) -> int:
    """Verifies the webhook"""
    challenge = request.query_params.get("hub.challenge")
    if challenge:
        monitor.append(
            EventLog(
                event="verification",
                data={"challenge": challenge},
                timestamp=str(datetime.now()),
            )
        )
        return challenge
    return {"error": "No challenge found"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    monitor.append(EventLog(event="notification", data=data, timestamp=str(datetime.now())))
    try:
        if "entry" in data and "changes" in data["entry"][0]:
            changes = data["entry"][0]["changes"]
            for change in changes:
                if change["field"] == "comments":
                    comment_id = change["value"]["id"]
                    reply_message = "Thank you for your comment!"
                    id = fbb.reply_to_comment(comment_id, reply_message)
                    if not id:
                        monitor.append(
                            EventLog(
                                event="reply",
                                data={"status": "failed to reply"},
                                timestamp=str(datetime.now()),
                            )
                        )
                        return {"status": "notification received, couldn't reply back"}
                    monitor.append(
                        EventLog(
                            event="reply",
                            data={"status": "replied"},
                            timestamp=str(datetime.now()),
                        )
                    )
                    return {"status": f"comment replied with id {id}"}
        monitor.append(
            EventLog(
                event="notification",
                data={"status": "ignored"},
                timestamp=str(datetime.now()),
            )
        )
        return {"status": "ignored"}
    except Exception as e:
        print(e)
        monitor.append(
            EventLog(
                event="notification",
                data={"status": f"unexpected response: {e}"},
                timestamp=str(datetime.now()),
            )
        )
        return {"status": "unexpected response"}


@app.get("/privacy")
async def privacy():
    return FileResponse(f"{BASE_DIR}/static/privacy.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9999, reload=True)
