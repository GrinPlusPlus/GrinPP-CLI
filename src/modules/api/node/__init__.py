#!/usr/bin/env python3

import requests

from modules.api import _get_process_status_error


def _node_rest_call(method: str, params: str = "") -> dict:
    node_rest_api_url = f"http://127.0.0.1:3413/v1/{method}{params}"
    try:
        return requests.get(url=node_rest_api_url).json()
    except requests.exceptions.ConnectionError:
        raise Exception(_get_process_status_error())


def _parse_status_response(data: dict) -> tuple[str, float]:
    message: str = ""
    percentage: float = 0.0

    if data["sync_status"] == "NOT_CONNECTED":
        message = "Waiting for Peers"
    elif data["sync_status"] == "FULLY_SYNCED":
        message = "Running"
        percentage = 100 * float(data["chain"]["height"]) / float(data["header_height"])
    elif data["sync_status"] == "SYNCING_HEADERS":
        message = "1/4 Syncing Headers"
        if data["network"]["height"] > 0:
            percentage = (
                100 * float(data["header_height"]) / float(data["network"]["height"])
            )
        else:
            percentage = 0
    elif data["sync_status"] == "DOWNLOADING_TXHASHSET":
        message = "2/4 Downloading State"
        if data["state"]["download_size"] > 0:
            percentage = (
                100
                * float(data["state"]["downloaded"])
                / float(data["state"]["download_size"])
            )
        else:
            percentage = 0
    elif data["sync_status"] == "PROCESSING_TXHASHSET":
        message = "3/4 Validating State"
        percentage = data["state"]["processing_status"]
    elif data["sync_status"] == "SYNCING_BLOCKS":
        message = "4/4 Syncing Blocks"
        if data["chain"]["height"] == 0 or data["chain"]["height"] == 0:
            percentage = 0
        elif data["header_height"] < 10080 or data["chain"]["height"] < 10080:
            percentage = (
                100 * float(data["chain"]["height"]) / float(data["header_height"])
            )
        elif data["header_height"] - data["chain"]["height"] > 10080:
            percentage = 0
        else:
            remaining = 100 * (
                (float(data["header_height"]) - float(data["chain"]["height"])) / 10080
            )
            if remaining <= 0:
                remaining = 1
            percentage = 100 - remaining

    return message, percentage
