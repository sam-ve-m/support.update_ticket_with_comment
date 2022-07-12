class InvalidJwtToken(Exception):
    msg = 'Failed to validate user credentials'


class InvalidTicketRequester(Exception):
    msg = 'Invalid ticket owner'


class TicketNotFound(Exception):
    msg = 'No tickets found'
