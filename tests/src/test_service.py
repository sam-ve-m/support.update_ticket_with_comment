from unittest.mock import patch
from zenpy.lib.api_objects import Comment
import pytest

from func.src.service import UpdateTicketWithComment
from .stubs import StubTicket, StubUser, StubGetUsers, StubAttachmentUploadInstance


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_user(mock_zenpy_client, client_update_comment_service):
    stub_user = StubGetUsers().append_user(StubUser(external_id=102030))
    mock_zenpy_client().users.return_value = stub_user
    user = client_update_comment_service.get_user()

    assert isinstance(user, StubUser)
    assert user.external_id == client_update_comment_service.x_thebes_answer["user"]["unique_id"]


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_user_if_zenpy_client_is_called(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.get_user()

    mock_zenpy_client.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_user_if_zenpy_client_users_is_called(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.get_user()

    mock_zenpy_client().users.assert_called_once_with(external_id=102030)


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_user_raises(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.x_thebes_answer["user"].update(unique_id=000000)
    mock_zenpy_client().users.return_value = None
    with pytest.raises(Exception, match="Bad request"):
        client_update_comment_service.get_user()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_ticket(mock_zenpy_client, client_update_comment_service):
    mock_zenpy_client().tickets.return_value = StubTicket(id=255)
    ticket = client_update_comment_service.get_ticket()

    assert isinstance(ticket, StubTicket)
    assert ticket.id == client_update_comment_service.params["id"]


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_ticket_if_zenpy_client_is_called(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.get_ticket()

    mock_zenpy_client.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_ticket_if_zenpy_client_tickets_is_called(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.get_ticket()

    mock_zenpy_client().tickets.assert_called_once_with(id=255)


@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket(requester=99))
@patch.object(UpdateTicketWithComment, "get_user", return_value=99)
def test_requester_is_the_same_ticket_user(mock_get_user, mock_get_ticket, client_update_comment_service):
    response = client_update_comment_service.requester_is_the_same_ticket_user()

    assert response is True
    assert mock_get_user() == mock_get_ticket().requester


@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket(requester=99))
@patch.object(UpdateTicketWithComment, "get_user", return_value=99)
def test_requester_is_the_same_ticket_user_if_get_user_is_called(mock_get_user, mock_get_ticket, client_update_comment_service):
    client_update_comment_service.requester_is_the_same_ticket_user()

    mock_get_user.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket(requester=99))
@patch.object(UpdateTicketWithComment, "get_user", return_value=99)
def test_requester_is_the_same_ticket_user_if_get_ticket_is_called(mock_get_user, mock_get_ticket, client_update_comment_service):
    client_update_comment_service.requester_is_the_same_ticket_user()

    mock_get_ticket.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket(requester="user123"))
@patch.object(UpdateTicketWithComment, "get_user", return_value="user456")
def test_requester_is_the_same_ticket_user_raises(mock_get_user, mock_get_ticket, client_update_comment_service):
    with pytest.raises(Exception, match="Bad request"):
        client_update_comment_service.requester_is_the_same_ticket_user()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_when_have_attachments_then_return_attachments_tokens(mock_zenpy_client, client_update_comment_service_with_attach):
    mock_zenpy_client().attachments.upload.return_value = StubAttachmentUploadInstance(token=10)
    attachment_tokens = client_update_comment_service_with_attach.get_attachments()

    assert attachment_tokens[0] == 10


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_attachments_if_zenpy_client_is_called(mock_zenpy_client, client_update_comment_service_with_attach):
    client_update_comment_service_with_attach.get_attachments()

    mock_zenpy_client.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_attachments_if_zenpy_client_upload_is_called(mock_zenpy_client, client_update_comment_service_with_attach):
    client_update_comment_service_with_attach.get_attachments()

    mock_zenpy_client().attachments.upload.assert_called_once()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_when_attachments_is_empty_then_return_empty_list(mock_zenpy_client, client_update_comment_service):
    attachment_tokens = client_update_comment_service.get_attachments()

    assert attachment_tokens == []


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
def test_get_attachments_when_zenpy_client_not_called(mock_zenpy_client, client_update_comment_service):
    client_update_comment_service.get_attachments()

    mock_zenpy_client.assert_not_called()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=['token99'])
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    assert isinstance(mock_get_ticket().comment, Comment)
    assert mock_get_ticket().comment.uploads[0] == 'token99'
    assert mock_get_ticket().comment.body == "corpo do comentário"
    assert mock_get_ticket().comment.author_id == 9
    assert mock_get_ticket().comment.public is True


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=StubAttachmentUploadInstance(token=9))
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment_if_get_user_is_called(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    mock_get_user.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=StubAttachmentUploadInstance(token=9))
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment_if_get_ticket_is_called(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    mock_get_ticket.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=StubAttachmentUploadInstance(token=9))
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment_if_get_attachments_is_called(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    mock_attachments.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=StubAttachmentUploadInstance(token=9))
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment_if_zenpy_client_is_called(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    mock_zenpy_client.assert_called_once_with()


@patch.object(UpdateTicketWithComment, "_get_zenpy_client")
@patch.object(UpdateTicketWithComment, "get_attachments", return_value=StubAttachmentUploadInstance(token=9))
@patch.object(UpdateTicketWithComment, "get_ticket", return_value=StubTicket())
@patch.object(UpdateTicketWithComment, "get_user", return_value=StubUser(id=9))
def test_update_comment_if_zenpy_client_tickets_update_is_called(
    mock_get_user,
    mock_get_ticket,
    mock_attachments,
    mock_zenpy_client,
    client_update_comment_service,
):
    client_update_comment_service.update_comments_in_zendesk_ticket()

    mock_zenpy_client().tickets.update.assert_called_once()
