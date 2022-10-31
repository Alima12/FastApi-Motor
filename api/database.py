import motor.motor_asyncio
from .config import settings
import certifi
from redis import Redis
import asyncio

loop = asyncio.new_event_loop()
client = motor.motor_asyncio.AsyncIOMotorClient("localhost", port=27017)
# client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url, certifi.where())
client.get_io_loop = asyncio.get_running_loop


async def get_db():
    return client.MyFastApi


redis_host = settings.redis_host
redis_port = settings.redis_port
redis_db = settings.redis_db
print(
    redis_host,
    redis_port,
    redis_db
)
redis_conn = Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
