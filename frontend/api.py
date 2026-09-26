import requests

BASE_URL = "http://localhost:8000"


def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": username,
            "password": password
        },
        timeout=10
    )

    return response