from typing import Optional, Union

from fastapi import APIRouter, Request, Response
from starlette.responses import FileResponse

from app.core import get_monitor_state, state
from app.schemas import EventLog, Message

router = APIRouter()

monitor = get_monitor_state()


@router.get("/", status_code=200)
async def home():
    return {"Hello": "World"}


@router.get("/monitor", status_code=200)
async def get_webhook_event_logs() -> list[EventLog]:
    """Returns the monitor state"""
    return monitor


@router.post("/post", status_code=201)
def post_message_to_instagram_account(
    message: Message, response: Response
) -> dict[str, Optional[str]]:
    """Sends a post to instagram"""
    id = state.fbb.send_post(message.message, message.image_url)

    if id:
        return {"post_id": id}
    response.status_code = 400
    return {"post_id": None}


@router.get("/webhook", status_code=200)
async def echo_back_verification_webhook(
    request: Request, response: Response
) -> Union[int, dict]:
    """Verifies the webhook by echoing back the challange code"""
    challenge = request.query_params.get("hub.challenge", None)
    if challenge:
        return challenge
    monitor.append(
        EventLog(
            event="webhook verification",
            data="verification failed, no challenge found",
        )
    )
    return 400


@router.post("/webhook", status_code=200)
async def process_new_comment_notification_webhook(
    request: Request, response: Response
):
    """Received new comment notification and processes the event"""
    data = await request.json()
    try:
        comment_id, _ = state.fbb.process_new_comment_notification(data)
        if not comment_id:
            monitor.append(
                EventLog(
                    event="new comment",
                    data="notification received, no comment id found",
                )
            )
            return 400

        reply_message = "Thank you for your comment!"
        id = state.fbb.reply_to_comment(comment_id, reply_message)
        if not id:
            monitor.append(
                EventLog(
                    event="reply to comment",
                    data="notification received, couldn't reply back",
                )
            )
            return 400
        monitor.append(
            EventLog(
                event="reply to comment",
                data=f"notification received, replied to comment {comment_id}",
            )
        )
        return 200

    except Exception as e:
        print(e)
        monitor.append(
            EventLog(
                event="new comment",
                data=f"notification received, error: {e}",
            )
        )
        return 400


@router.get("/privacy")
async def privacy():
    return FileResponse(f"{state.base_path}/static/privacy.html")
