import re
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.errors import DuplicateKeyError, NetworkTimeout

from api.schemas import User, UserResponse, UpdateUser, Tokens
from fastapi.encoders import jsonable_encoder
from api.utils import hash_password
from api.database import get_db
from api.oauth2 import create_auth_tokens
from fastapi_jwt_auth import AuthJWT
from api.config import settings

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)


@router.get("/", response_model=List[UserResponse])
async def users_list(db = Depends(get_db)):
    users = db.users.find()
    users = await users.to_list(length=10)
    return users


@router.get("/get/me/", response_model=UserResponse)
async def get_me(Authorize: AuthJWT = Depends(), db = Depends(get_db)):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    user = await db.users.find_one({"_id": current_user_id})
    if user:
        return user

    raise HTTPException(404, "User Not Found!")


@router.get("/{username}", response_model=UserResponse)
async def get_one(username:str, db = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    user = await db.users.find_one({"_id": current_user_id})
    if not user["is_admin"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You don't have permission")

    user = await db.users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User not found!")
    return user


@router.post("/register", response_description="Register User", response_model=Tokens, status_code=status.HTTP_201_CREATED)
async def new_user(user: User, db=Depends(get_db)):
    try:
        user.password = hash_password(user.password)
        user = jsonable_encoder(user)
        user["is_admin"] = False
        await db.users.insert_one(user)
        token = create_auth_tokens(user['_id'], fresh=True)
        return token

    except DuplicateKeyError as e:
        error_field_name = next(iter(e.details["keyPattern"]))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'{error_field_name.title()} already exists.')
    except NetworkTimeout:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timed out.")


 
@router.put("/put", response_description="Update User", response_model=UserResponse)
async def update_user(new_data: UpdateUser, db=Depends(get_db), Authorize:AuthJWT=Depends()):
    Authorize.fresh_jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    user = await db.users.find_one({"_id": current_user_id})
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    new_data = jsonable_encoder(new_data)
    if not re.match(settings.email_regex, new_data["email"]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Please enter a valid email")

    await db["users"].update_one({"username": user["username"]}, {"$set": new_data})
    updated_user = await db["users"].find_one({"username": user["username"]})
    return updated_user


@router.delete("/delete_account/", status_code=204)
async def delete_account(db=Depends(get_db), Authorize: AuthJWT=Depends()):
    Authorize.fresh_jwt_required()
    current_user_id = Authorize.get_jwt_subject()
    user = await db.users.find_one({"_id": current_user_id})
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    await db.users.delete_one({"username": {"$eq": user["username"]}})



