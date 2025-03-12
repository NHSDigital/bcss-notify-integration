from time import time
import uuid
import requests

from util import Util


class AuthManager:

    def __init__(self, token_url: str, private_key: str) -> None:
        self.private_key = private_key
        self.base_url = token_url

    def get_access_token(self) -> str:

        jwt: str = self.generate_auth_jwt()

        headers: dict = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt,
        }

        response = requests.request(
            'POST', self.base_url,
            headers=headers,
            data=body,
            timeout=10
        ).json()

        access_token = response["access_token"]

        return access_token

    def generate_auth_jwt(self) -> str:
        algorithm: str = "RS512"

        expiry_minutes: int = 5

        headers: dict = {"alg": algorithm, "typ": "JWT", "kid": "test-int-1"}

        payload: dict = {
            "sub": "xpDldjaJYydBAvZUh0M8g35wJWGvZTOr",
            "iss": "xpDldjaJYydBAvZUh0M8g35wJWGvZTOr",
            "jti": str(uuid.uuid4()),
            "aud": "https://int.api.service.nhs.uk/oauth2/token",
            "exp": int(time()) + 300,  # 5mins in the future
        }

        return Util.generate_jwt(
            algorithm, self.private_key, headers, payload, expiry_minutes=expiry_minutes
        )
