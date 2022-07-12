# Jormungandr
from func.src.services.update_ticket import UpdateTicketWithComment
from tests.src.img import attachment1
from tests.src.stubs import stub_unique_id, stub_ticket_comments_validated

# Third party
from pytest import fixture


@fixture(scope="function")
def client_update_comment_service():
    client_update_comment_service = UpdateTicketWithComment(
        unique_id=stub_unique_id,
        ticket_comments_validated=stub_ticket_comments_validated
    )
    return client_update_comment_service


@fixture(scope="function")
def client_update_comment_service_with_attach():
    client_update_comment_service = UpdateTicketWithComment(
        unique_id=stub_unique_id,
        ticket_comments_validated=stub_ticket_comments_validated
    )
    client_update_comment_service.params["attachments"].append(attachment1)
    return client_update_comment_service
