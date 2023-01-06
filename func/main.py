# Jormungandr
from func.src.domain.enum import CodeResponse
from func.src.domain.exceptions import InvalidJwtToken, TicketNotFound, InvalidTicketRequester
from func.src.domain.response.model import ResponseModel
from func.src.domain.validator import TicketComments
from func.src.services.update_ticket import UpdateTicketWithComment
from func.src.services.jwt import JwtService

# Standards
from http import HTTPStatus

# Third party
from etria_logger import Gladsheim
from flask import request


async def update_ticket_comments():
    message = "Jormungandr::update_ticket_comments"
    raw_ticket_comments = request.json
    jwt = request.headers.get("x-thebes-answer")
    try:
        ticket_comments_validated = TicketComments(**raw_ticket_comments).dict()
        await JwtService.apply_authentication_rules(jwt=jwt)
        unique_id = await JwtService.decode_jwt_and_get_unique_id(jwt=jwt)
        comments_service = UpdateTicketWithComment(
            ticket_comments_validated=ticket_comments_validated,
            unique_id=unique_id,
        )
        comments_service.update_in_ticket()
        response_model = ResponseModel.build_response(
            success=True,
            code=CodeResponse.SUCCESS,
            message="The ticket was successfully updated",
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.OK
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
            status=HTTPStatus.OK
        )
        return response

    except InvalidTicketRequester as ex:
        Gladsheim.error(error=ex, message=f"{message}::No ticket was found with the specified id")
        response_model = ResponseModel.build_response(
            message=ex.msg,
            success=False,
            code=CodeResponse.INVALID_OWNER,
        )
        response = ResponseModel.build_http_response(
            response_model=response_model,
            status=HTTPStatus.UNAUTHORIZED
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
