from pydantic import BaseModel
from typing import List
from .enums import TicketType


class Base64Attachments(BaseModel):
    name: str
    content: str


class Ticket(BaseModel):
    subject: str
    description: str
    ticket_type: TicketType
    attachments: List[Base64Attachments] = []
