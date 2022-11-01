from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from fastapi import Body
from api.config import settings
import re
import pydantic


class PyObjectID(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectID")

        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: PyObjectID=Field(default_factory=PyObjectID, alias="_id")
    username: str = Body(..., regex=settings.username_regex)
    email: str = Body(..., regex=settings.email_regex)
    password: str = Field(...)

    @pydantic.validator("username", "email")
    def validate_identifier(cls, value):
        return value.lower()

    class Config:
        allowed_population_by_field_name=True
        arbitrary_types_allowed=True
        json_encoders={ObjectId:str}
        schema_extra = {
            "example":{
                "username": "Ali",
                "email":"test@example.com",
                "password": "password"
            }
        }


class UserResponse(BaseModel):
    username: str=Field(...)
    email: EmailStr=Field(...)
    is_admin: bool = False

    @pydantic.validator("username", "email")
    def validate_identifier(cls, value):
        return value.lower()

    class Config:
        allowed_population_by_field_name=True
        arbitrary_types_allowed=True
        json_encoders={ObjectId:str}
        schema_extra = {
            "example":{
                "username": "Ali",
                "email":"test@example.com"
            }
        }
        

class UpdateUser(BaseModel):
    email: EmailStr=Field(...)
    class Config:
        allowed_population_by_field_name=True
        arbitrary_types_allowed=True
        json_encoders={ObjectId:str}
        schema_extra = {
            "example":{
                "email":"test@example.com"
            }
        }


class Tokens(BaseModel):
    access_token:str
    refresh_token:str
    type:str = "Bearer"


class LoginSchema(BaseModel):
    identifier: str
    password: str

    @pydantic.validator("identifier")
    def validate_identifier(cls, value):
        if re.fullmatch(settings.email_regex, value):
            return value
        elif re.fullmatch(settings.username_regex, value):
            return value.lower()

        raise ValueError("Identifier is not valid!")

    class Config:
        schema_extra = {
                "example": {
                    "identifier": "test@example.com",
                    "password": "password"
                }
        }