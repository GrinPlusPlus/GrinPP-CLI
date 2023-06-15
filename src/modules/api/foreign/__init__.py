#!/usr/bin/env python3

import uuid

import requests

from modules.api import _get_process_status_error


def _owner_foreign_rpc_call(method: str, params: dict = {}) -> dict:
    owner_foreign_rpc_url = "http://127.0.0.1:3413/v2/foreign"

    call_params = {
        "jsonrpc": "2.0",
        "method": method,
        "id": str(uuid.uuid4()),
        "params": params,
    }

    try:
        data: dict = requests.post(url=owner_foreign_rpc_url, json=call_params).json()
        if "error" in data:
            raise Exception(data["error"]["message"])
        return data
    except requests.exceptions.ConnectionError:
        raise Exception(_get_process_status_error())
