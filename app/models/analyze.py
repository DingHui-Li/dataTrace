from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Analyze(BaseModel):
    date:str
    create_time:int
    summary:str
    emotion_score:int
    emotion_desc:str
    topic:str
    urls:str
    keywords:str

    class Config:
        from_attributes = True