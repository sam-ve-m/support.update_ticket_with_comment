from pydantic import BaseModel
from typing import List


class Base64Attachments(BaseModel):
    name: str
    content: str


class CommentValidator(BaseModel):
    body: str
    attachments: List[Base64Attachments] = []
    id: int

