import json
from time import time
import uuid
import os

from BaseAPIClient import BaseAPIClient
from Util import Util


class AuthManager:

    def __init__(self, token_url: str, private_key: str) -> None:
        self.api_client: BaseAPIClient = BaseAPIClient(token_url)
        self.PRIVATE_KEY = private_key

    def get_access_token(self) -> str:

        jwt: str = self.generate_auth_jwt()

        headers: dict = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt,
        }

        reponse = self.api_client.make_request(
            "POST", "", data=body, headers=headers, params=None
        )
        access_token = reponse["access_token"]

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
            algorithm, self.PRIVATE_KEY, headers, payload, expiry_minutes=5
        )
