from uuid import uuid4
from rich import print
import requests


def call_owner_rpc_v3(method: str, params: dict = {}) -> dict:
    url = "http://127.0.0.1:3420/v3/owner"

    params = {
        "jsonrpc": "2.0",
        "method": method,
        "id": str(uuid4()),
        "params": params,
    }

    response = requests.post(url=url, json=params).json()
    if "error" in response:
        raise Exception(response["error"]["message"])
    ##print(response["result"])
    return response["result"]["Ok"]
