from pydantic import BaseModel, Field
from uuid import uuid4


class QuestionResponse(BaseModel):
    response: str


class AskInput(BaseModel):
    question: str
    responses: "list[str]" = []


class TaskInput(BaseModel):
    topic: str
