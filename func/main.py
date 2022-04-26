# Jormungandr
from src.enum import CodeResponse
from src.exceptions import InvalidJwtToken, InvalidUniqueId, TicketNotFound
from src.service import UpdateTicketWithComment
from src.validator import CommentValidator

# Standards
from http import HTTPStatus
from json import dumps

# Third party
from etria_logger import Gladsheim
from flask import Response, request
from heimdall_client.bifrost import Heimdall
import asyncio

event_loop = asyncio.get_event_loop()


def update_ticket_comments():
    message = "Jormungandr::update_ticket_comments"
    url_path = request.full_path
    x_thebes_answer = request.headers.get("x-thebes-answer")
    heimdall_client = Heimdall()
    raw_ticket_params = request.get_json()
    try:
        is_a_valid_jwt = event_loop.run_until_complete(
            heimdall_client.validate_jwt(jwt=x_thebes_answer)
        )
        if is_a_valid_jwt:
            jwt_content, heimdall_status = event_loop.run_until_complete(
                heimdall_client.decode_payload(jwt=x_thebes_answer)
            )
            comment_params = CommentValidator(**raw_ticket_params)
            update_comments_service = UpdateTicketWithComment(
                params=comment_params,
                url_path=url_path,
                x_thebes_answer=jwt_content["decoded_jwt"],
            )
            ticket_updated = update_comments_service()
            response = Response(
                dumps(
                    {
                        "result": None,
                        "message": "The information was successfully updated",
                        "success": ticket_updated,
                        "code": CodeResponse.SUCCESS.value,
                    }
                ),
                mimetype="application/json",
                status=HTTPStatus.OK.value,
            )
            return response
        raise InvalidJwtToken

    except InvalidJwtToken as ex:
        Gladsheim.error(error=ex, message=f"{message}::Invalid JWT token")
        response = Response(
            dumps(
                {
                    "result": None,
                    "message": ex.msg,
                    "success": False,
                    "code": CodeResponse.JWT_INVALID.value,
                }
            ),
            mimetype="application/json",
            status=HTTPStatus.UNAUTHORIZED.value,
        )
        return response

    except InvalidUniqueId as ex:
        Gladsheim.error(error=ex, message=f"{message}::'The JWT unique id is not the same user unique id'")
        response = Response(
            dumps(
                {
                    "result": None,
                    "message": ex.msg,
                    "success": False,
                    "code": CodeResponse.JWT_INVALID.value,
                }
            ),
            mimetype="application/json",
            status=HTTPStatus.UNAUTHORIZED.value,
        )
        return response

    except TicketNotFound as ex:
        Gladsheim.error(error=ex, message=f"{message}::No ticket was found with the specified id")
        response = Response(
            dumps(
                {
                    "result": None,
                    "message": ex.msg,
                    "success": False,
                    "code": CodeResponse.DATA_NOT_FOUND.value,
                }
            ),
            mimetype="application/json",
            status=HTTPStatus.NOT_FOUND.value,
        )
        return response

    except ValueError as ex:
        Gladsheim.error(ex=ex, message=f'{message}::There are invalid format or extra parameters')
        response = Response(
            dumps(
                {
                    "result": None,
                    "message": "There are invalid format or extra parameters",
                    "success": False,
                    "code": CodeResponse.INVALID_PARAMS.value,
                }
            ),
            mimetype="application/json",
            status=HTTPStatus.BAD_REQUEST.value,
        )
        return response

    except Exception as ex:
        Gladsheim.error(error=ex, message=f"{message}::{str(ex)}")
        response = Response(
            dumps(
                {
                    "result": None,
                    "message": "Unexpected error occurred",
                    "success": False,
                    "code": CodeResponse.INTERNAL_SERVER_ERROR.value,
                }
            ),
            mimetype="application/json",
            status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )
        return response
