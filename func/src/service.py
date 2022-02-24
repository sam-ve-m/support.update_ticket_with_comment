from decouple import config
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Via, Comment, Attachment
from typing import Optional


class UpdateTicketWithComment:
    zenpy_client = Zenpy(**{
        'email': config('ZENDESK_EMAIL'),
        'password': config('ZENDESK_PASSWORD'),
        'subdomain': config('ZENDESK_SUBDOMAIN')
    })

    def __init__(self, params, url_path, x_thebes_answer):
        self.x_thebes_answer = x_thebes_answer
        self.url_path = url_path
        self.params = params.dict()
        pass

    def get_ticket(self) -> Ticket:
        ticket_zenpy = self.zenpy_client.tickets(id=self.params['id'])
        return ticket_zenpy

    def get_user(self) -> User:
        unique_id = self.xthebes_answer['unique_id']
        user_result = self.zenpy_client.users(external_id=unique_id)
        if user_result:
            user_zenpy = user_result.values[0]
            return user_zenpy
        else:
            raise Exception('Invalid user')

    def requester_is_the_same_ticket_user(self) -> bool:
        user_zenpy = self.get_user()
        ticket_zenpy = self.get_ticket()
        if ticket_zenpy.requester == user_zenpy:
            return True
        return False

    def get_comments(self) -> Comment:
        ticket_zenpy = self.get_ticket()
        comments_zenpy = self.zenpy_client.tickets.comments(ticket=ticket_zenpy)
        return comments_zenpy

    def update_comments_in_zendesk_ticket(self):
        user_zenpy = self.get_user()
        ticket_zenpy = self.get_ticket()
        attachment_tokens = self.get_attachments()
        new_comment = Comment(
            author_id=user_zenpy.id,
            body=self.params['description'],
            uploads=attachment_tokens,
            public=True
        )
        ticket_zenpy.comment = new_comment
        self.zenpy_client.tickets.update(ticket_zenpy)
