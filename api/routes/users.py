from typing import List
from fastapi import APIRouter, HTTPException
from api.schemas import User, db, UserResponse, UpdateUser
from fastapi.encoders import jsonable_encoder
from api.utils import hash_password
import secrets

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)

@router.get("/", response_model=List[UserResponse])
async def users_list():
    users = db.temp_users.find()
    users = await users.to_list(length=10)
    return users


@router.get("/{username}", response_model=UserResponse)
async def get_one(username:str):
    user = await db.temp_users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User not found!")
    return user


@router.post("/register", response_description="Register User", response_model=UserResponse)
async def new_user(user:User):
    user = jsonable_encoder(user)
    username_found = await db["temp_users"].find_one({"username":user["username"]})
    email_found = await db["temp_users"].find_one({"email":user["email"]})
    if username_found or email_found:
        raise HTTPException(409, "User is already Exists")

    user["password"] = hash_password(user["password"])
    user["apiKey"] = secrets.token_hex(30)
    new_user = await db["temp_users"].insert_one(user)
    created_user = await db["temp_users"].find_one({"_id": new_user.inserted_id})
    return created_user

 
@router.put("/put", response_description="Update User", response_model=UserResponse)
async def update_user(username:str, new_data:UpdateUser):
    new_data = jsonable_encoder(new_data)
    user = await db.temp_users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User Not found")
    new_user = await db["temp_users"].update_one({"username": username}, {"$set":new_data})
    updated_user = await db["temp_users"].find_one({"username": username})
    return updated_user


@router.delete("/{username}", status_code=204)
async def delete_user(username:str):
    user = await db.temp_users.find_one({"username":{"$eq":username}})
    if not user:
        raise HTTPException(404, "User not found!")

    await db.temp_users.delete_one({"username": {"$eq": username}})
    
    return user

 