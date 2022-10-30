import json
from api.main import app
import pytest
from httpx import AsyncClient
import asyncio


@pytest.fixture
def anyio_backend():
    return 'asyncio'


class TestUser:
    access_token = ""
    refresh_token = ""

    @pytest.mark.anyio
    async def test_user_login(self):
        async with AsyncClient(app=app, base_url="http://localhost:8000", ) as ac:
            ac.get_io_loop = asyncio.get_running_loop
            response = await ac.post("/auth/login", data=json.dumps({"identifier": "alim","password":"password"}), headers={"X-Token": "hailhydra"})
            keys = response.json().keys()
            assert "access_token" in keys
            assert "refresh_token" in keys
            assert "type" in keys
            assert response.status_code == 200
            token = response.json()["access_token"]
            self.access_token = response.json()["access_token"]
            await self.use_protected_endpoint(token)



    @pytest.mark.anyio
    async def test_login_fails(self):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            ac.get_io_loop = asyncio.get_running_loop
            response = await ac.post("/auth/login", data=json.dumps({"password":"password"}), headers={"X-Token": "hailhydra"})
            keys = response.json().keys()
            assert response.status_code == 422


    @pytest.mark.anyio
    async def use_protected_endpoint(self, token):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            ac.get_io_loop = asyncio.get_running_loop
            headers= {
                "token": token,
            }
            protected_endpoint = await ac.get("/users/get/me/", headers=headers)
            user = protected_endpoint.json().keys()
            assert protected_endpoint.status_code == 200
            assert "email" in user
            assert "username" in user
            assert "password" not in user
            assert "_id" not in user    


