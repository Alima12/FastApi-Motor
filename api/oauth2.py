from uuid import uuid4
from fastapi_jwt_auth import AuthJWT

from api.schemas import Tokens


def create_auth_tokens(sub, fresh: bool = False):
    Authorize = AuthJWT()
    auth = Authorize.create_pair_token(sub, fresh=fresh)
    return Tokens(**auth)
