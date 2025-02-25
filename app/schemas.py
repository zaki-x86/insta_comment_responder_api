from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class Message(BaseModel):
    """
    Stores message data to be posted on Instagram. It uses a default image in case none is given.
    """

    message: str
    image_url: Optional[str] = (
        "https://techspotproxy.com/wp-content/uploads/2019/03/test-img.png"
    )


class EventLog(BaseModel):
    """
    Stores event data processed via webhooks
    """

    event: str
    data: Union[str, dict]
    timestamp: Optional[str] = str(datetime.now().isoformat())
