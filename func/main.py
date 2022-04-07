from flask import Response, request
from json import dumps
import asyncio

from etria_logger import Gladsheim
from heimdall_client.bifrost import Heimdall
from src.validator import CommentValidator
from src.service import UpdateTicketWithComment

event_loop = asyncio.get_event_loop()


def update_ticket_comments():
    url_path = request.full_path
    x_thebes_answer = request.headers.get('x-thebes-answer')
    heimdall_client = Heimdall()
    raw_ticket_params = request.get_json()
    try:
        http_status = 403
        inserted = False
        is_a_valid_jwt = event_loop.run_until_complete(heimdall_client.validate_jwt(jwt=x_thebes_answer))
        if is_a_valid_jwt:
            jwt_content, heimdall_status = event_loop.run_until_complete(
                heimdall_client.decode_payload(jwt=x_thebes_answer)
            )
            comment_params = CommentValidator(**raw_ticket_params)
            update_comments_service = UpdateTicketWithComment(
                params=comment_params,
                url_path=url_path,
                x_thebes_answer=jwt_content['decoded_jwt'],
            )
            update_comments_service()
            http_status = 200
            inserted = True
            response = Response(
                dumps({'status': inserted}),
                mimetype='application/json',
                status=http_status,
            )
        return response
    except Exception as error:
        message = 'Fission: update_ticket_comments'
        Gladsheim.error(error, message)
        response = Response(
            dumps({'error': {'message': error}, 'status': False}),
            mimetype='application/json',
            status=400,
        )
        return response
