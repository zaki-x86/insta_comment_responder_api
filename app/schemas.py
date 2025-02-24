from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    message: str
    image_url: Optional[str] = "https://techspotproxy.com/wp-content/uploads/2019/03/test-img.png"
