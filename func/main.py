from logging import getLogger
from flask import Response, request
from json import dumps
from heimdall_client.bifrost import Heimdall
from src.validator import Ticket
log = getLogger()


def update_new_ticket_comments_in_zendesk(ticket_id):
    x_thebes_answer = request.headers.get('x-thebes-answer')
    heimdall_client = Heimdall(logger=log)
    raw_ticket_params = request.json
    http_status = 403
    try:
        inserted = False
        http_status = 200
        if heimdall_client.validate_jwt(jwt=x_thebes_answer):
            jwt_content, heimdall_status = heimdall_client.decode_payload(jwt=x_thebes_answer)
            ticket_params = Ticket(**raw_ticket_params)

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