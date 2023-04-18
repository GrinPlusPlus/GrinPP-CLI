#!/usr/bin/env python3

import uuid

import requests

from modules.api import _get_process_status_error


def _owner_wallet_rpc_call(method: str, params: dict = {}) -> dict:
    owner_wallet_rpc_url = "http://127.0.0.1:3421/v2"

    call_params = {
        "jsonrpc": "2.0",
        "method": method,
        "id": str(uuid.uuid4()),
        "params": params,
    }

    try:
        response: requests.Response = requests.post(
            url=owner_wallet_rpc_url, json=call_params
        )
        if len(response.text) > 0:
            data = response.json()
            if "error" in data:
                raise Exception(data["error"]["message"])
            return data["result"]
        return {}
    except requests.exceptions.ConnectionError:
        raise Exception(_get_process_status_error())


def _filter_transactions_by_status(transactions: list, status: str):
    transactions.sort(key=lambda t: t["creation_date_time"], reverse=True)

    if status == "coinbase":
        return filter(lambda t: "coinbase" in str(t["type"]).lower(), transactions)
    elif status == "sent":
        return filter(lambda t: "sent" in str(t["type"]).lower(), transactions)
    elif status == "pending":
        return filter(
            lambda t: "sending" in str(t["type"]).lower()
            or "receiving" in str(t["type"]).lower(),
            transactions,
        )
    elif status == "received":
        return filter(lambda t: str(t["type"]).lower() == "received", transactions)
    elif status == "canceled":
        return filter(lambda t: "canceled" in str(t["type"]).lower(), transactions)
    else:
        return transactions
