import json
import os
import time
import urllib.error
import urllib.request


OPEN_WEBUI_URL = "http://open-webui:8080"

ADMIN_EMAIL = os.environ["OPENWEBUI_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["OPENWEBUI_ADMIN_PASSWORD"]

API_KEY_FILE = "/shared/openwebui_api_key"


def request(method, url, data=None, token=None):
    headers = {
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request_object = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(request_object) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8")

        print(f"Open WebUI returned HTTP {error.code}")
        print(f"Response: {response_body}")

        raise
    
    
def wait_for_open_webui():
    print("Waiting for Open WebUI...")

    while True:
        try:
            request(
                "GET",
                f"{OPEN_WEBUI_URL}/health"
            )

            print("Open WebUI is ready.")
            return

        except Exception:
            time.sleep(2)


def generate_api_key():
    print("Logging into Open WebUI...")

    login_response = request(
        "POST",
        f"{OPEN_WEBUI_URL}/api/v1/auths/signin",
        {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )

    token = login_response.get("token")

    if not token:
        raise RuntimeError(
            f"Login succeeded but no token was returned: {login_response}"
        )

    print("Login successful.")

    print("Generating Open WebUI API key...")

    api_key_response = request(
        "POST",
        f"{OPEN_WEBUI_URL}/api/v1/auths/api_key",
        token=token
    )

    api_key = api_key_response.get("api_key")

    if not api_key:
        raise RuntimeError(
            f"API key was not returned: {api_key_response}"
        )

    return api_key


def wait_for_api_key_to_work(api_key):
    print("Waiting for Open WebUI API to accept the API key...")

    while True:
        try:
            request(
                "GET",
                f"{OPEN_WEBUI_URL}/api/v1/models",
                token=api_key
            )

            print("Open WebUI API is ready.")
            return

        except Exception:
            time.sleep(2)


def main():
    if os.path.exists(API_KEY_FILE):
        print("Open WebUI API key already exists.")
        print("Reusing existing API key.")

        with open(API_KEY_FILE) as file:
            api_key = file.read().strip()

        wait_for_api_key_to_work(api_key)
        return

    wait_for_open_webui()

    api_key = generate_api_key()

    with open(API_KEY_FILE, "w") as file:
        file.write(api_key)

    print("Open WebUI API key generated successfully.")

    wait_for_api_key_to_work(api_key)


if __name__ == "__main__":
    main()