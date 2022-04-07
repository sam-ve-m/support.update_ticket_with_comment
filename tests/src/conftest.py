from pytest import fixture

from func.src.service import UpdateTicketWithComment
from func.src.validator import CommentValidator
from.img import attachment1

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
