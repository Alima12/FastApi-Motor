from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
import certifi

client = motor.motor_asyncio.AsyncIOMotorClient("localhost", port=27017)
db = client.MyFastApi


loop = client.get_io_loop()
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
    username: str=Field(...)
    email: EmailStr=Field(...)
    password: str = Field(...)

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
    id: PyObjectID=Field(default_factory=PyObjectID, alias="_id")
    username: str=Field(...)
    email: EmailStr=Field(...)

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
    identifier:str
    password:str

    class Config:
            schema_extra = {
            "example":{
                "identifier":"test@example.com",
                "password": "password"
            }
        }