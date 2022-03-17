from unittest.mock import Mock, patch
import pytest

from func.src.service import UpdateTicketWithComment
from func.src.validator import CommentValidator, Base64Attachments


jwt_test = {'user': {'unique_id': 102030}}
params_test = {'id': 255, 'body': 'corpo do comentário', 'attachments': []}


class UpdateCommentBuilder:
    def __init__(self):
        self.url_path = ''
        self.x_thebes_answer = {'user': {'unique_id': 102030}}
        self.params = CommentValidator(**params_test)

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
        for attachment in attachments:
            self.params['attachments'].append(attachment)
        return self


class StubUser:
    def __init__(self):
        self.external_id = None

    def set_external_id(self, external_id: int):
        self.external_id = external_id
        return self


class StubGetUsers:
    def __init__(self):
        self.values = []

    def append_user(self, stub_user: StubUser):
        self.values.append(stub_user)
        return self


def test_get_user_ticket1():
    params_data_builder = (
        UpdateCommentBuilder()
        .set_x_thebes_answer(jwt_test)
        .set_params(params_test)
    )
    stub_user = StubUser().append_values(123)
    attrs = {'users.return_value': stub_user}
    mock_zenpy_client = Mock(**attrs)
    b = mock_zenpy_client
    c = mock_zenpy_client()
    a = mock_zenpy_client().users()

    # UpdateTicketWithComment._get_zenpy_client = mock_zenpy_client

    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    client_update_ticket_service._get_zenpy_client = mock_zenpy_client
    user = client_update_ticket_service.get_user()
    assert user == 123


@patch('func.src.service.Zenpy')
def test_get_user_ticket(mock_zenpy_client):
    params_data_builder = (
        UpdateCommentBuilder()
        .set_x_thebes_answer(jwt_test)
        .set_params(params_test)
    )
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
     # attrs = {'users.return_value': StubUser().append_values(123)}
    # mock_zenpy_client.configure_mock(**attrs)
    mock_zenpy_client().users(return_value=StubUser().set_external_id(123))
    # client_update_ticket_service._get_zenpy_client().users = MagicMock(
    #     return_value=StubUser().append_values(123)
    # )
    user = client_update_ticket_service.get_user()
    mock_zenpy_client.assert_called()
    # mock_zenpy_client.users.assert_called_once()
    # client_update_ticket_service._get_zenpy_client().users.assert_called_once()
    # assert client_update_ticket_service.x_thebes_answer["user"]["unique_id"] == 102030
    # assert user == 123
    # assert mock_zenpy_client.call_count == 3


@patch('func.src.service.Zenpy')
def test_get_user(mock_zenpy_client):
    stube_user = StubGetUsers().append_user(StubUser().set_external_id(102030))
    mock_zenpy_client().users.return_value = stube_user
    params_data_builder = UpdateCommentBuilder()
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    user = client_update_ticket_service.get_user()

    assert user.external_id == 102030
    assert user.external_id == client_update_ticket_service.x_thebes_answer['user']['unique_id']
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
    assert client_update_ticket_service.x_thebes_answer['user']['unique_id'] == 999
    with pytest.raises(Exception, match='Invalid user'):
        user = client_update_ticket_service.get_user()




