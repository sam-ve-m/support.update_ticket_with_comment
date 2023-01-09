# Jormungandr
from ..domain.exceptions import InvalidJwtToken

# Third party
from heimdall_client import Heimdall


class JwtService:

    @classmethod
    async def decode_jwt_and_get_unique_id(cls, jwt: str) -> str:
        jwt_content, heimdall_status_response = await Heimdall.decode_payload(jwt=jwt)
        unique_id = jwt_content["decoded_jwt"]['user'].get('unique_id')
        return unique_id

    @classmethod
    async def apply_authentication_rules(cls, jwt: str):
        is_valid_jwt = await Heimdall.validate_jwt(jwt=jwt)
        if not is_valid_jwt:
            raise InvalidJwtToken
