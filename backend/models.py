from pydantic import BaseModel
from typing import List, Dict, Optional

class ImageTag(BaseModel):
    filename: str
    tag: str

class PromptRequest(BaseModel):
    description: str
    tags: List[ImageTag]
    canvas_size: Optional[str] = "1080x1080"
    generate_gif: Optional[bool] = False

class FeedbackRequest(BaseModel):
    remarks: str
    previous_json: Dict
