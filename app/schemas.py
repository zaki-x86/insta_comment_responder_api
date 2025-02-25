from pydantic import BaseModel
from typing import Union, Optional
from datetime import datetime

class Message(BaseModel):
    message: str
    image_url: Optional[str] = "https://techspotproxy.com/wp-content/uploads/2019/03/test-img.png"

class EventLog(BaseModel):
    event: str
    data: Union[str, dict]
    timestamp: Optional[str] = str(datetime.now().isoformat())
