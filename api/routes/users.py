from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from api.schemas import User, UserResponse, UpdateUser, Tokens
from fastapi.encoders import jsonable_encoder
from api.utils import hash_password
import secrets
from api.database import get_db
from api.oauth2 import create_auth_tokens
from fastapi_jwt_auth import AuthJWT

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
async def get_one(username:str, db = Depends(get_db)):
    user = await db.users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User not found!")
    return user


@router.post("/register", response_description="Register User", response_model=Tokens)
async def new_user(user:User, db = Depends(get_db)):
    user = jsonable_encoder(user)
    username_found = await db["users"].find_one({"username":user["username"]})
    email_found = await db["users"].find_one({"email":user["email"]})
    if username_found or email_found:
        raise HTTPException(409, "User is already Exists")

    user["password"] = hash_password(user["password"])
    new_user = await db["users"].insert_one(user)
    auth_result = create_auth_tokens(new_user.inserted_id, True)
    return auth_result

 
@router.put("/put", response_description="Update User", response_model=UserResponse)
async def update_user(username:str, new_data:UpdateUser, db = Depends(get_db)):
    new_data = jsonable_encoder(new_data)
    user = await db.users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User Not found")
    await db["users"].update_one({"username": username}, {"$set":new_data})
    updated_user = await db["users"].find_one({"username": username})
    return updated_user


@router.delete("/{username}", status_code=204)
async def delete_user(username:str, db = Depends(get_db)):
    user = await db.users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User not found!")

    await db.users.delete_one({"username": {"$eq": username}})
    
    return user


