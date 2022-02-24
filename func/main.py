from logging import getLogger
from flask import Response, request
from json import dumps
from heimdall_client.bifrost import Heimdall
from src.validator import Ticket
from src.service import UpdateTicketWithComment
log = getLogger()


def update_new_ticket_comments_in_zendesk():
    url_path = request.full_path
    x_thebes_answer = request.headers.get('x-thebes-answer')
    heimdall_client = Heimdall(logger=log)
    raw_ticket_params = request.json
    try:
        http_status = 403
        inserted = False
        if heimdall_client.validate_jwt(jwt=x_thebes_answer):
            jwt_content, heimdall_status = heimdall_client.decode_payload(jwt=x_thebes_answer)
            ticket_params = Ticket(**raw_ticket_params)
            update_comments_service = UpdateTicketWithComment(params=ticket_params, url_path=url_path, x_thebes_answer=jwt_content['decoded_jwt'])
            update_comments_service.requester_is_the_same_ticket_user()
            update_comments_service.update_comments_in_zendesk_ticket()
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