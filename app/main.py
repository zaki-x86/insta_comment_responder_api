import os
from typing import Optional

from decouple import config
from fastapi import FastAPI, Request
from starlette.responses import FileResponse

from app.schemas import Message
from app.service import FBBService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="Task API",
    description="API to post to Instagram",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

fbb = FBBService(
    access_token=config("META_DEVELOPER_ACCESS_TOKEN"),
    insta_account=config("INSTAGRAM_ACCOUNT_ID"),
)


@app.on_event("startup")
def on_startup():
    pass


@app.get("/")
async def read_root():
    return {"Hello": "World"}


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
        return challenge
    return {"error": "No challenge found"}


@app.get("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "hub.challenge" in data:
        return data["hub.challenge"]  # Respond to Facebook's initial verification
    elif "entry" in data and "changes" in data["entry"][0]:
        changes = data["entry"][0]["changes"]
        for change in changes:
            if change["field"] == "comments":
                comment_id = change["value"]["comment_id"]
                # Respond to the comment with a static message
                # Implement the logic to reply to the comment
                reply_message = "Thank you for your comment!"
                return {"status": "comment replied"}
    return {"status": "ignored"}


@app.get("/privacy")
async def privacy():
    return FileResponse(f"{BASE_DIR}/static/privacy.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9999, reload=True)
