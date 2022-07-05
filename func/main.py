# Jormungandr
from src.domain.enum import CodeResponse
from src.domain.exceptions import InvalidJwtToken, InvalidUniqueId, TicketNotFound
from src.domain.response.model import ResponseModel
from src.domain.validator import CommentValidator
from src.services.update_ticket import UpdateTicketWithComment
from src.services.jwt import JwtService

# Standards
from http import HTTPStatus

# Third party
from etria_logger import Gladsheim
from flask import request


def update_ticket_comments():
    message = "Jormungandr::update_ticket_comments"
    url_path = request.full_path
    raw_ticket_params = request.json
    jwt = request.headers.get("x-thebes-answer")
    try:
        comment_params = CommentValidator(**raw_ticket_params)
        JwtService.apply_authentication_rules(jwt=jwt)
        decoded_jwt = JwtService.decode_jwt(jwt=jwt)
        update_comments_service = UpdateTicketWithComment(
            params=comment_params,
            url_path=url_path,
            decoded_jwt=decoded_jwt,
        )
        success = update_comments_service()
        response_model = ResponseModel.build_response(
            success=success,
            code=CodeResponse.SUCCESS,
            message="The information was successfully updated",
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.OK
        )
        return response

    except InvalidUniqueId as ex:
        Gladsheim.error(error=ex, message=f"{message}::'The JWT unique id is not the same user unique id'")
        response_model = ResponseModel.build_response(
            message=ex.msg,
            success=False,
            code=CodeResponse.JWT_INVALID,
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.UNAUTHORIZED
        )
        return response

    except TicketNotFound as ex:
        Gladsheim.error(error=ex, message=f"{message}::No ticket was found with the specified id")
        response_model = ResponseModel.build_response(
            message=ex.msg,
            success=False,
            code=CodeResponse.DATA_NOT_FOUND,
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.NOT_FOUND
        )
        return response

    except InvalidJwtToken as ex:
        Gladsheim.error(error=ex, message=f"{message}::Invalid JWT token")
        response_model = ResponseModel.build_response(
            success=False,
            code=CodeResponse.JWT_INVALID,
            message=ex.msg,
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.UNAUTHORIZED
        )
        return response

    except ValueError as ex:
        Gladsheim.error(ex=ex, message=f'{message}::There are invalid format or extra parameters')
        response_model = ResponseModel.build_response(
            success=False,
            code=CodeResponse.INVALID_PARAMS,
            message="There are invalid format or extra/missing parameters",
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.BAD_REQUEST
        )
        return response

    except Exception as ex:
        Gladsheim.error(error=ex, message=f"{message}::{str(ex)}")
        response_model = ResponseModel.build_response(
            success=False,
            code=CodeResponse.INTERNAL_SERVER_ERROR,
            message="Unexpected error occurred",
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )
        return response
