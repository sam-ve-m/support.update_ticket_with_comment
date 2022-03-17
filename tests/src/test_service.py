from unittest.mock import patch

import func.src.service
import pytest

from func.src.service import UpdateTicketWithComment
from func.src.validator import CommentValidator, Base64Attachments
from img import attachment1, attachment2

jwt_test = {'user': {'unique_id': 102030}}
params_test = {'id': 255, 'body': 'corpo do comentário', 'attachments': []}


class UpdateCommentBuilder:
    def __init__(self):
        self.url_path = ''
        self.x_thebes_answer = {'user': {'unique_id': 102030}}
        self.params = CommentValidator(**params_test).dict()

    def set_url_path(self, url_path: str):
        self.url_path = url_path
        return self

    def set_x_thebes_answer(self, jwt: dict):
        self.x_thebes_answer = jwt
        return self

    def set_unique_id(self, unique_id: int):
        self.x_thebes_answer['user'].update(unique_id=unique_id)
        return self

    def set_params(self, params: dict):
        self.params = CommentValidator(**params)
        return self

    def set_params_id(self, ticket_id: int):
        self.params = self.params.update(id=ticket_id)

    def set_params_body(self, body: str):
        self.params = self.params.update(body=body)
        return self

    def append_params_attachments(self, attachments: Base64Attachments):
        self.params['attachments'].append(attachments)
        return self


class StubUser:
    def __init__(self):
        self.id = None
        self.external_id = None
        self.requester = None

    def set_external_id(self, external_id: int):
        self.external_id = external_id
        return self

    def set_requester(self, requester_user):
        self.requester = requester_user
        return self

    def set_id(self, user_id: int):
        self.id = user_id
        return self


class StubGetUsers:
    def __init__(self):
        self.values = []

    def append_user(self, stub_user: StubUser):
        self.values.append(stub_user)
        return self


class StubAttachmentUploadInstance:
    def __init__(self):
        self.token = None

    def set_token(self, token):
        self.token = token
        return self


class StubTicket:
    pass


@patch('func.src.service.Zenpy')
def test_get_user(mock_zenpy_client):
    stub_user = StubGetUsers().append_user(StubUser().set_external_id(102030))
    mock_zenpy_client().users.return_value = stub_user
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    user = client_update_ticket_service.get_user()

    assert user.external_id == 102030
    assert (
        user.external_id
        == client_update_ticket_service.x_thebes_answer['user']['unique_id']
    )
    assert mock_zenpy_client is func.src.service.Zenpy
    mock_zenpy_client.assert_called()
    mock_zenpy_client().users.assert_called_once_with(external_id=102030)


@patch('func.src.service.Zenpy')
def test_get_user_raises(mock_zenpy_client):
    mock_zenpy_client().users.return_value = None
    params_data_builder = UpdateCommentBuilder().set_unique_id(999)
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )

    assert (
        client_update_ticket_service.x_thebes_answer['user']['unique_id']
        == 999
    )
    with pytest.raises(Exception, match='Invalid user'):
        client_update_ticket_service.get_user()


@patch('func.src.service.Zenpy')
def test_get_ticket(mock_zenpy_client):
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    mock_zenpy_client().tickets.return_value = (
        client_update_ticket_service.params['id']
    )
    ticket = client_update_ticket_service.get_ticket()

    assert ticket == 255
    mock_zenpy_client.assert_called()
    mock_zenpy_client().tickets.assert_called_once_with(id=255)


@patch.object(
    UpdateTicketWithComment,
    'get_ticket',
    return_value=StubUser().set_requester(requester_user='user123'),
)
@patch.object(UpdateTicketWithComment, 'get_user', return_value='user123')
def test_requester_is_the_same_ticket_user(mock_get_user, mock_get_ticket):
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    response = client_update_ticket_service.requester_is_the_same_ticket_user()
    assert response is True
    mock_get_ticket.assert_called_once()
    mock_get_user.assert_called_once()
    assert mock_get_user() == mock_get_ticket().requester


@patch.object(
    UpdateTicketWithComment,
    'get_ticket',
    return_value=StubUser().set_requester(requester_user='user123'),
)
@patch.object(UpdateTicketWithComment, 'get_user', return_value='user456')
def test_requester_is_the_same_ticket_user_raises(
    mock_get_user, mock_get_ticket
):
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    with pytest.raises(Exception, match='Bad request'):
        client_update_ticket_service.requester_is_the_same_ticket_user()


@patch('func.src.service.Zenpy')
def test_when_attachments_is_empty_then_return_empty_list(mock_zenpy_client):
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    attachment_tokens = client_update_ticket_service.get_attachments()

    assert client_update_ticket_service.params['attachments'] == []
    assert attachment_tokens == []
    mock_zenpy_client.assert_not_called()


@patch('func.src.service.Zenpy')
def test_when_have_attachments_then_return_attachments_tokens(
    mock_zenpy_client,
):
    params_data_builder = UpdateCommentBuilder().append_params_attachments(attachment1)
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    mock_zenpy_client().attachments.upload.return_value= StubAttachmentUploadInstance().set_token(10)
    attachment_tokens = client_update_ticket_service.get_attachments()

    assert client_update_ticket_service.params['attachments'][0]['name'] == attachment1['name']
    assert client_update_ticket_service.params['attachments'][0]['content'] == attachment1['content']
    assert attachment_tokens[0] == 10
    mock_zenpy_client.assert_called()
    mock_zenpy_client().attachments.upload.assert_called_once()


patch.object(UpdateTicketWithComment, 'get_ticket', return_value='')
@patch.object(UpdateTicketWithComment, 'get_user', return_value=StubUser().set_id(9))
def test_update_comment():
    pass
