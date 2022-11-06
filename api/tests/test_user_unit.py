import unittest
from api.main import app
from api.database import get_db
import motor.motor_asyncio
import asyncio
from fastapi.testclient import TestClient
import json

test_client = motor.motor_asyncio.AsyncIOMotorClient("localhost", port=27017)


def get_test_db():
    test_client.get_io_loop = asyncio.get_running_loop
    return test_client.TestMyFastApi


access_token = ""
new_access_token = ""
refresh_token = ""


def make_order():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare


ordered, compare = make_order()
unittest.defaultTestLoader.sortTestMethodsUsing = compare


class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app.dependency_overrides[get_db] = get_test_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        test_client.get_io_loop = asyncio.new_event_loop
        test_client.drop_database("TestMyFastApi")
        del app.dependency_overrides[get_db]

    @ordered
    def test_main(self):
        response = self.client.get("/")
        self.assertEqual(response.json(), {"msg": "Hello World"})
        self.assertEqual(response.status_code, 200)

    @ordered
    def test_register(self):
        response = self.client.post(
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

        self.assertEqual(response.status_code, 201)
        keys = response.json().keys()
        self.assertIn("access_token", keys)
        self.assertIn("refresh_token", keys)
        self.assertIn("type", keys)

    @ordered
    def test_login(self):
        global access_token, refresh_token
        response = self.client.post(
            "/auth/login",
            data=json.dumps(
                {
                    "identifier": "aliali.ali1378@yahoo.com",
                    "password": "password"
                }
            ),
            headers={"X-Token": "Hello world"}
        )
        self.assertEqual(response.status_code, 200)
        keys = response.json().keys()
        self.assertIn("access_token", keys)
        self.assertIn("refresh_token", keys)
        self.assertIn("type", keys)
        access_token, refresh_token = response.json()["access_token"], response.json()["refresh_token"]

    @ordered
    def test_get_me(self):
        global access_token
        headers = {
            "token": access_token
        }
        protected_endpoint = self.client.get("/users/get/me/", headers=headers)
        user = protected_endpoint.json().keys()
        self.assertEqual(protected_endpoint.status_code, 200)
        self.assertIn("email", user)
        self.assertIn("username", user)
        self.assertNotIn("password", user)
        self.assertNotIn("_id", user)

    @ordered
    def test_revoke_refresh_token(self):
        global access_token, refresh_token, new_access_token
        headers = {
            "token": refresh_token,
            'accept': 'application/json'
        }
        protected_endpoint = self.client.post("/auth/refresh", headers=headers)
        self.assertEqual(protected_endpoint.status_code, 200)
        new_access_token = protected_endpoint.json()["access_token"]
        keys = protected_endpoint.json().keys()
        self.assertIn("access_token", keys)
        self.assertIn("refresh_token", keys)
        self.assertIn("type", keys)

    @ordered
    def test_get_refresh_token_by_revoked_token(self):
        headers = {
            "token": refresh_token
        }
        protected_endpoint = self.client.post("/auth/refresh", headers=headers)
        self.assertEqual(protected_endpoint.json(), {"detail": "Token has been revoked"})
        self.assertEqual(protected_endpoint.status_code, 401)

    @ordered
    def test_get_me_by_revoked_token(self):
        global access_token
        headers = {
            "token": access_token
        }
        protected_endpoint = self.client.get("/users/get/me/", headers=headers)
        self.assertEqual(protected_endpoint.json(), {"detail": "Token has been revoked"})
        self.assertEqual(protected_endpoint.status_code, 401)

    @ordered
    def test_get_me_by_new_token(self):
        global new_access_token
        headers = {
            "token": new_access_token
        }
        protected_endpoint = self.client.get("/users/get/me/", headers=headers)
        user = protected_endpoint.json().keys()
        self.assertEqual(protected_endpoint.status_code, 200)
        self.assertIn("email", user)
        self.assertIn("username", user)
        self.assertNotIn("password", user)
        self.assertNotIn("_id", user)


if __name__ == "__main__":
    unittest.main()
