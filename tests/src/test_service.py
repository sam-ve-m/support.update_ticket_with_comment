from unittest.mock import Mock, MagicMock, patch
from zenpy import Zenpy
from func.src.service import UpdateTicketWithComment
from func.src.validator import CommentValidator, Base64Attachments
import pytest

jwt_test = {'user': {'unique_id': 102030}}
params_test = {'id': 255, 'body': 'teste_teste', 'attachments': []}


class UpdateCommentBuilder:
    def __init__(self):
        self.url_path = ''
        self.x_thebes_answer = None
        self.params = None

    def set_url_path(self, url_path):
        self.url_path = url_path

    def set_x_thebes_answer(self, jwt):
        self.x_thebes_answer = jwt
        return self

    def set_unique_id(self, unique_id):
        self.x_thebes_answer = self.x_thebes_answer['user'].update(
            unique_id=unique_id
        )
        return self

    def set_params(self, params):
        self.params = CommentValidator(**params)
        return self

    def set_params_id(self, ticket_id):
        self.params = self.params.update(id=ticket_id)

    def set_params_body(self, body):
        self.params = self.params.update(body=body)
        return self

    def set_params_attachments(self, attachments):
        self.params = self.params.update(
            attachments=Base64Attachments(**attachments)
        )


class StubUser:
    def __init__(self):
        self.values = []

    def append_values(self, value):
        self.values.append(value)
        return self


class StubZenpyClient:
    def __init__(self):
        self.users = None

    pass


@patch.object(UpdateTicketWithComment, '_get_zenpy_client')
def test_get_user_ticket(mock_zenpy):
    params_data_builder = (
        UpdateCommentBuilder()
        .set_x_thebes_answer(jwt_test)
        .set_params(params_test)
    )
    mock_zenpy_client = Mock()
    UpdateTicketWithComment._get_zenpy_client = mock_zenpy_client
    mock_zenpy_client.users = MagicMock(return_value=StubUser('BLABLA'))
    client_update_ticket_service = UpdateTicketWithComment(
        x_thebes_answer=params_data_builder.x_thebes_answer,
        params=params_data_builder.params,
        url_path=params_data_builder.url_path,
    )
    user = client_update_ticket_service.get_user()


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
    client_update_ticket_service._get_zenpy_client = mock_zenpy_client
    client_update_ticket_service._get_zenpy_client().users = MagicMock(
        return_value=StubUser().append_values(123)
    )

    user = client_update_ticket_service.get_user()
    client_update_ticket_service._get_zenpy_client().users.assert_called_once()
    client_update_ticket_service._get_zenpy_client.assert_called()
    mock_zenpy_client.assert_called()
    assert client_update_ticket_service.x_thebes_answer["user"]["unique_id"] == 102030
    assert user == 123
    assert mock_zenpy_client.call_count == 3

