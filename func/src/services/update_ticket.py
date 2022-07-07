# Jormungandr
from ..domain.exceptions import TicketNotFound, InvalidTicketRequester

# Standards
from base64 import b64decode
from os import SEEK_SET
from tempfile import TemporaryFile
from typing import List

# Third party
from decouple import config
from etria_logger import Gladsheim
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Comment, Attachment


class UpdateTicketWithComment:
    zenpy_client = None

    @classmethod
    def _get_zenpy_client(cls):
        if cls.zenpy_client is None:
            try:
                cls.zenpy_client = Zenpy(
                    **{
                        "email": config("ZENDESK_EMAIL"),
                        "password": config("ZENDESK_PASSWORD"),
                        "subdomain": config("ZENDESK_SUBDOMAIN"),
                    }
                )
            except Exception as ex:
                message = (
                    "_get_zenpy_client::error to get Zenpy Client"
                )
                Gladsheim.error(error=ex, message=message)
                raise ex
        return cls.zenpy_client

    def __init__(self, ticket_comments_validated: dict, unique_id: str):
        self.unique_id = unique_id
        self.params = ticket_comments_validated

    def get_attachments(self) -> List[Attachment]:
        attachment_tokens = list()
        for attachment in self.params["attachments"]:
            file_bytes = b64decode(attachment["content"])
            with TemporaryFile() as temp_file:
                temp_file.write(file_bytes)
                temp_file.seek(SEEK_SET)
                zenpy_client = self._get_zenpy_client()
                upload_instance = zenpy_client.attachments.upload(
                    fp=temp_file, target_name=attachment["name"]
                )
                attachment_tokens.append(upload_instance.token)
        return attachment_tokens

    def get_ticket(self) -> Ticket:
        zenpy_client = self._get_zenpy_client()
        try:
            ticket_zenpy = zenpy_client.tickets(id=self.params["id"])
            return ticket_zenpy
        except Exception as ex:
            message = f'get_ticket::There is no ticket with this id {self.params["id"]}'
            Gladsheim.error(message=message, error=ex)
            raise TicketNotFound

    def get_user(self) -> User:
        zenpy_client = self._get_zenpy_client()
        user_result = zenpy_client.users(external_id=self.unique_id)
        if user_result:
            user_zenpy = user_result.values[0]
            return user_zenpy

    def _requester_is_the_same_ticket_user(self) -> bool:
        user_zenpy = self.get_user()
        ticket_zenpy = self.get_ticket()
        if ticket_zenpy.requester == user_zenpy:
            return True
        message = (
            f"requester_is_the_same_ticket_user::Requester is not the ticket owner::"
            f"Requester:{ticket_zenpy.requester}::Ticket owner user:{user_zenpy}"
        )
        Gladsheim.info(message=message)
        raise InvalidTicketRequester

    def update_in_ticket(self) -> bool:
        self._requester_is_the_same_ticket_user()
        user_zenpy = self.get_user()
        ticket_zenpy = self.get_ticket()
        attachment_tokens = self.get_attachments()
        new_comment = Comment(
            author_id=user_zenpy.id,
            body=self.params["body"],
            uploads=attachment_tokens,
            public=True,
        )
        ticket_zenpy.comment = new_comment
        zenpy_client = self._get_zenpy_client()
        zenpy_client.tickets.update(ticket_zenpy)
        return True
