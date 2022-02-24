from enum import Enum


class TicketType(Enum):
    PROBLEM = 'problem'
    INCIDENT = 'incident'
    QUESTION = 'question'
    TASK = 'task'
