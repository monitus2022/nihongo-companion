import requests

class RequestHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.get(url, **kwargs)

    def post(self, endpoint: str, json: dict, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return requests.post(url, json=json, **kwargs)
