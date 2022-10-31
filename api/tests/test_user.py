import json
from api.main import app
from httpx import AsyncClient
import asyncio
import pytest


@pytest.fixture
def anyio_backend():
    return 'asyncio'


access_token = ""
refresh_token = ""


class TestUser:
    @pytest.mark.anyio
    @pytest.mark.order(2)
    async def test_user_login(self):
        global access_token, refresh_token
        async with AsyncClient(app=app, base_url="http://test", ) as ac:
            response = await ac.post(
                "/auth/login",
                data=json.dumps(
                    {
                        "identifier": "alimakk9764995511",
                        "password": "password"
                    }
                ),
                headers={"X-Token": "Hello world"}
            )
            keys = response.json().keys()
            assert "access_token" in keys
            assert "refresh_token" in keys
            assert "type" in keys
            assert response.status_code == 200
            access_token, refresh_token = response.json()["access_token"], response.json()["refresh_token"]

    @pytest.mark.anyio
    @pytest.mark.order(1)
    async def test_login_fails(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            ac.get_io_loop = asyncio.get_running_loop()
            response = await ac.post(
                "/auth/login",
                data=json.dumps(
                    {"password": "password"}
                ),
                headers={"X-Token": "hello world"}
            )
            assert response.status_code == 422

    @pytest.mark.anyio
    @pytest.mark.order(after="TestUser::test_user_login")
    async def test_get_me(self):
        global access_token
        async with AsyncClient(app=app, base_url="http://test") as ac:
            headers = {
                "token": access_token,
            }
            protected_endpoint = await ac.get("/users/get/me/", headers=headers)
            user = protected_endpoint.json().keys()
            assert protected_endpoint.status_code == 200
            assert "email" in user
            assert "username" in user
            assert "password" not in user
            assert "_id" not in user

    @pytest.mark.anyio
    @pytest.mark.order(after="TestUser::test_user_login")
    async def test_revoke_refresh_token(self):
        global access_token, refresh_token
        async with AsyncClient(app=app, base_url="http://test") as ac:
            headers = {
                "token": refresh_token,
                'accept': 'application/json'
            }
            protected_endpoint = await ac.post("/auth/refresh", headers=headers)
            tokens = protected_endpoint.json().keys()
            assert protected_endpoint.status_code == 200
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            assert "type" in tokens

        async with AsyncClient(app=app, base_url="http://test") as ac:
            headers = {
                "token": refresh_token
            }
            protected_endpoint = await ac.post("/auth/refresh", headers=headers)
            assert protected_endpoint.json() == {"detail": "Token has been revoked"}
            assert protected_endpoint.status_code == 401

        async with AsyncClient(app=app, base_url="http://test") as ac:
            headers = {
                "token": access_token,
            }
            protected_endpoint = await ac.get("/users/get/me/", headers=headers)
            assert protected_endpoint.json() == {"detail": "Token has been revoked"}
            assert protected_endpoint.status_code == 401