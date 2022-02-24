from base64 import b64decode
from os import SEEK_SET
from tempfile import TemporaryFile
from decouple import config
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Via, Comment, Attachment
from typing import List, Optional
from pydantic import BaseModel


class UpdateTicketWithComment:
    zenpy_client = Zenpy(**{
        'email': config('ZENDESK_EMAIL'),
        'password': config('ZENDESK_PASSWORD'),
        'subdomain': config('ZENDESK_SUBDOMAIN')
        })

    def __init__(self, params: BaseModel, url_path: str, x_thebes_answer: dict):
        self.x_thebes_answer = x_thebes_answer
        self.url_path = url_path
        self.params = params.dict()
        #Sindri.dict_to_primitive_types(self.params)

    def get_ticket(self) -> Ticket:
        ticket_zenpy = self.zenpy_client.tickets(id=self.params['id'])
        return ticket_zenpy

    def get_user(self) -> User:
        unique_id = self.x_thebes_answer['unique_id']
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
        raise Exception('Bad request')

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

    def get_attachments(self) -> List[Attachment]:
        attachment_tokens = list()
        for attachment in self.params['attachments']:
            file_bytes = b64decode(attachment['content'])
            with TemporaryFile() as temp_file:
                temp_file.write(file_bytes)
                temp_file.seek(SEEK_SET)
                upload_instance = self.zenpy_client.attachments.upload(
                    fp=temp_file,
                    target_name=attachment['name']
                )
                attachment_tokens.append(upload_instance.token)
        return attachment_tokens

    def get_comments(self) -> Comment:
        ticket_zenpy = self.get_ticket
        comments_zenpy = self.zenpy_client.tickets.comments(ticket=ticket_zenpy)
        return comments_zenpy