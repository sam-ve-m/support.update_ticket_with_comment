# Standards
from typing import List
from re import match

# Third party
from pydantic import BaseModel, validator


class Base64Attachments(BaseModel):
    name: str
    content: str

    @validator("content", always=True, allow_reuse=True)
    def validate_content(cls, content):
        base_64_regex = r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$'
        if match(base_64_regex, content) and content != "":
            return content
        raise ValueError("Base64 file content are invalid")


class TicketComments(BaseModel):
    body: str
    attachments: List[Base64Attachments] = []
    id: int
