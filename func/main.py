from logging import getLogger
from flask import Response, request
from json import dumps
from heimdall_client.bifrost import Heimdall
from src.validator import CommentValidator
from src.service import UpdateTicketWithComment
import asyncio

log = getLogger()
event_loop = asyncio.get_event_loop()


def fn():
    url_path = request.full_path
    x_thebes_answer = request.headers.get("x-thebes-answer")
    heimdall_client = Heimdall(logger=log)
    raw_ticket_params = request.json
    try:
        http_status = 403
        inserted = False
        is_a_valid_jwt = event_loop.run_until_complete(heimdall_client.validate_jwt(jwt=x_thebes_answer))
        if is_a_valid_jwt:
            jwt_content, heimdall_status = event_loop.run_until_complete(heimdall_client.decode_payload(
                jwt=x_thebes_answer
            ))
            comment_params = CommentValidator(**raw_ticket_params)
            update_comments_service = UpdateTicketWithComment(
                params=comment_params,
                url_path=url_path,
                x_thebes_answer=jwt_content["decoded_jwt"],
            )
            update_comments_service()
            http_status = 200
        return Response(
            dumps({"status": inserted}),
            mimetype="application/json",
            status=http_status,
        )
    except Exception as e:
        log.error(str(e), exc_info=e)
        return Response(
            dumps({"error": {"message": str(e)}, "status": False}),
            mimetype="application/json",
            status=400,
        )
