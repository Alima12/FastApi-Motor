import motor.motor_asyncio
from .config import settings
import certifi


client = motor.motor_asyncio.AsyncIOMotorClient("localhost", port=27017)
# client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url, certifi.where())


async def get_db():
    return client.MyFastApi