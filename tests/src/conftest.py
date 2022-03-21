from pytest import fixture

from func.src.service import UpdateTicketWithComment
from func.src.validator import CommentValidator
from.img import attachment1


class StubUser:
    def __init__(self, id=None, external_id=None):
        self.id = id or None
        self.external_id = external_id or None

    def __repr__(self):
        return f'StubUser(id="{self.id}", external_id="{self.external_id}")'


class StubGetUsers:
    def __init__(self, values=None):
        self.values = values or []

    def append_user(self, stub_user: StubUser):
        self.values.append(stub_user)
        return self

    def __repr__(self):
        return f'StubGetUsers(values="{self.values}")'


class StubAttachmentUploadInstance:
    def __init__(self, token=None):
        self.token = token or None

    def __repr__(self):
        return f'StubAttachmentUploadInstance(token="{self.token}")'


class StubTicket:
    def __init__(self, comment=None, id=None, requester=None):
        self.comment = comment or None
        self.id = id or None
        self.requester = requester or None

    def __repr__(self):
        return f'StubTicket(comment="{self.comment}", id="{self.id}", requester="{self.requester}")'


jwt_test = {"user": {"unique_id": 102030}}
params_test = {"id": 255, "body": "corpo do comentário", "attachments": []}


@fixture(scope="function")
def client_update_comment_service():
    client_update_comment_service = UpdateTicketWithComment(
        x_thebes_answer=jwt_test,
        params=CommentValidator(**params_test),
        url_path="",
    )
    return client_update_comment_service


@fixture(scope="function")
def client_update_comment_service_with_attach():
    client_update_comment_service = UpdateTicketWithComment(
        x_thebes_answer=jwt_test,
        params=CommentValidator(**params_test),
        url_path="",
    )
    client_update_comment_service.params["attachments"].append(attachment1)
    return client_update_comment_service
