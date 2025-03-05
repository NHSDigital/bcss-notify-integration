import requests


class BaseAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        json: dict = None,
        headers: dict = None,
        params: dict = None,
    ) -> dict:
        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method,
            url,
            headers=headers,
            data=data,
            json=json,
            params=params,
            timeout=160,
        )

        return response.json()
