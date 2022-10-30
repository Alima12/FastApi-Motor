# import asyncio
# from fastapi.testclient import TestClient
# from unittest import TestCase
# from api.main import app
# import random as rn


# class TestUser(TestCase):
#     def setUp(self) -> None:
#         self.client = TestClient(app)
#         self.user_id = ""

#     def test_read_main(self):
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"msg": "Hello World"})
#         print("hi")


#     # @asyncio.coroutine
#     def test_read_users(self):
#         response = self.client.get("/users")
#         self.assertIsInstance(response.json(), list)
#         self.assertEqual(response.status_code, 200)


#     # @asyncio.coroutine
#     def test_create_user(self):
#         id = rn.randint(0,10000000000)
#         response = self.client.post(
#             "/users/register",
#             headers={"X-Token": "coneofsilence"},
#             json={"email": f"alimaklki{id}@gmail.com", "username": f"alimakk{id}", "password": "password"}
#         )

#         self.assertEqual(response.status_code, 201)
#         self.assertIn("access_token", response.json().keys())
#         self.assertIn("refresh_token", response.json().keys())
#         self.assertIn("type", response.json().keys())


# from fastapi.testclient import TestClient
import json
from api.main import app
# import random as rn


# client = TestClient(app)


# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# def test_create_user():
#     id = rn.randint(0,10000000000)
#     response = client.post(
#         "/users/register",
#         headers={"X-Token": "coneofsilence"},
#         json={"email": f"alimaklki{id}@gmail.com", "username": f"alimakk{id}", "password": "password"}
#     )

#     assert response.status_code == 201
#     assert "access_token" in response.json().keys()
#     assert "refresh_token" in response.json().keys()
#     assert "type" in response.json().keys()


import pytest
from httpx import AsyncClient
import asyncio
# import warnings
# from trio import TrioDeprecationWarning
# warnings.filterwarnings(action='ignore', category=TrioDeprecationWarning)


# @pytest.mark.anyio
# async def test_users_list():
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
#         response = await ac.get("/users", headers={"X-Token": "coneofsilence"})
#         print(response.json())
#
#     # assert response.status_code == 200
#     # assert type(response.json()) == list
#     assert True
    # pytest_sessionfinish(session)


# @pytest.mark.anyio
# async def test_main_page():
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
#         response = await ac.get("/")
#         print(response)
#
#     assert response.json() == {"msg": "Hello World"}
#     assert response.status_code == 200

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
@pytest.fixture
def anyio_backend():
    return 'asyncio'


access_token = ""


@pytest.mark.anyio
async def test_user_login():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        ac.get_io_loop = asyncio.get_running_loop
        response = await ac.post("/auth/login", data=json.dumps({"identifier": "alimakk9764995511","password":"password"}), headers={"X-Token": "hailhydra"})
        keys = response.json().keys()

        assert response.status_code == 200

        access_token = response.json()["access_token"]


@pytest.mark.anyio
async def test_login_fails():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        ac.get_io_loop = asyncio.get_running_loop
        response = await ac.post("/auth/login", data=json.dumps({"password":"password"}), headers={"X-Token": "hailhydra"})
        keys = response.json().keys()
        # assert "access_token" in keys
        # assert "refresh_token" in keys
        # assert "type" in keys
        assert response.status_code == 422


