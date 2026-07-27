from pydantic import BaseModel


class AITextResponse(BaseModel):
    text: str
