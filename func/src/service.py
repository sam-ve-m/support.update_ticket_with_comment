# Jormungandr
from .validator import CommentValidator
from .exceptions import InvalidUniqueId, TicketNotFound, InvalidTicketRequester

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

    def __init__(self, params: CommentValidator, url_path: str, x_thebes_answer: dict):
        self.x_thebes_answer = x_thebes_answer
        self.url_path = url_path
        self.params = params.dict()

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
        unique_id = self.x_thebes_answer["user"]["unique_id"]
        zenpy_client = self._get_zenpy_client()
        user_result = zenpy_client.users(external_id=unique_id)
        if user_result:
            user_zenpy = user_result.values[0]
            return user_zenpy
        message = (
            f"get_user::There is no user with this unique id specified"
            f"::{self.x_thebes_answer['user']['unique_id']}"
        )
        Gladsheim.error(message=message)
        raise InvalidUniqueId

    def requester_is_the_same_ticket_user(self) -> bool:
        user_zenpy = self.get_user()
        ticket_zenpy = self.get_ticket()
        if ticket_zenpy.requester == user_zenpy:
            return True
        message = (
            f"requester_is_the_same_ticket_user::Requester is not the ticket owner::"
            f"Requester:{ticket_zenpy.requester}::Ticket owner user:{user_zenpy}"
        )
        Gladsheim.error(message=message)
        raise InvalidTicketRequester

    def update_comments_in_zendesk_ticket(self) -> bool:
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

    def __call__(self, *args, **kwargs):
        self.requester_is_the_same_ticket_user()
        self.update_comments_in_zendesk_ticket()
