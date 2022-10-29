from fastapi import APIRouter, HTTPException, Depends, status
from api.schemas import UserResponse, Tokens
from fastapi.encoders import jsonable_encoder
from api.utils import verify_password
from api.database import get_db, redis_conn
from api.oauth2 import create_auth_tokens
from fastapi_jwt_auth import AuthJWT
from api.schemas import LoginSchema
from api.config import settings
from pymongo.errors import NetworkTimeout
import re

router = APIRouter(
    tags=["Authentication"],
    prefix="/auth"
)


denylist = set()

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    auth_id = decrypted_token['aid']
    entry = redis_conn.get(auth_id)
    return entry and entry == 'true'


@router.post("/login", response_model=Tokens)
async def login(user:LoginSchema, db = Depends(get_db)):
    email_regex_pattern = settings.email_regex
    username_regex_pattern = settings.username_regex
    found_user = None
    try:
        if re.fullmatch(email_regex_pattern, user.identifier):
            found_user = await db.users.find_one({"email": user.identifier})
        elif re.fullmatch(username_regex_pattern, user.identifier):
            found_user = await db.users.find_one({"username": user.identifier})
    except NetworkTimeout:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timed out.")

    if not found_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User and password doesn't match.")
    elif verify_password(user.password, found_user['password']):
        token = create_auth_tokens(found_user['_id'], fresh=True)
        return token


@router.post('/refresh')
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user_id = Authorize.get_jwt_subject()
    auth_id = Authorize.get_raw_jwt()['aid']
    redis_conn.setex(auth_id, settings.authjwt_refresh_token_expires, 'true')
    token = create_auth_tokens(current_user_id)

    return token

    
    
    