from uuid import uuid4

import requests


def call_owner_rpc_v2(method: str, params: dict = {}) -> dict:
    url = "http://127.0.0.1:3413/v2/owner"

    params = {"jsonrpc": "2.0", "method": method, "id": str(uuid4()), "params": params}

    response = requests.post(url=url, json=params)

    data = response.json()

    if "error" in data:
        raise Exception(data["error"]["message"])

    return data["result"]["Ok"]
