import json
from api.main import app
from httpx import AsyncClient
import asyncio
import pytest
from api.database import get_db
import motor.motor_asyncio


test_client = motor.motor_asyncio.AsyncIOMotorClient("localhost", port=27017)


def get_test_db():
    test_client.get_io_loop = asyncio.get_running_loop
    return test_client.TestMyFastApi


@pytest.fixture
def anyio_backend():
    return 'asyncio'


access_token = ""
refresh_token = ""


class TestUser:
    @classmethod
    def setup_class(cls):
        test_client.drop_database("TestMyFastApi")
        app.dependency_overrides[get_db] = get_test_db

    @classmethod
    def teardown_class(cls):
        del app.dependency_overrides[get_db]

    @pytest.mark.anyio
    @pytest.mark.order(1)
    async def test_register(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/users/register",
                data=json.dumps(
                    {
                        "email": "aliali.ali1378@yahoo.com",
                        "username": "alim",
                        "password": "password"
                    }
                ),
                headers={"X-Token": "Hello world"}
            )

            assert response.status_code == 201
            keys = response.json().keys()
            assert "access_token" in keys
            assert "refresh_token" in keys
            assert "type" in keys

    @pytest.mark.anyio
    @pytest.mark.order(3)
    async def test_user_login(self):
        global access_token, refresh_token
        async with AsyncClient(app=app, base_url="http://test", ) as ac:
            response = await ac.post(
                "/auth/login",
                data=json.dumps(
                    {
                        "identifier": "aliali.ali1378@yahoo.com",
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
    @pytest.mark.order(2)
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
            _token = protected_endpoint.json()["access_token"]
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

        access_token = _token

    @pytest.mark.anyio
    @pytest.mark.order(after="TestUser::test_revoke_refresh_token")
    async def test_delete_user(self):
        global access_token
        async with AsyncClient(app=app, base_url="http://test") as ac:
            headers = {
                "token": access_token,
            }
            protected_endpoint = await ac.delete("/users/delete_account/", headers=headers)
            assert protected_endpoint.status_code == 401
            assert protected_endpoint.json() == {"detail": "Fresh token required"}




