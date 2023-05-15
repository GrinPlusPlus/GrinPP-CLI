#!/usr/bin/env python3

import requests

from modules.api import _get_process_status_error


def _node_rest_call(method: str, params: str = "") -> dict:
    node_rest_api_url = f"http://127.0.0.1:3413/v1/{method}{params}"
    try:
        return requests.get(url=node_rest_api_url).json()
    except requests.exceptions.ConnectionError:
        raise Exception(_get_process_status_error())


"""
{
  "chain": {
    "hash": "000181a8336f6ae49ba314083c3e5a817a335616e0e0ad204db28733fd825b52",
    "height": 2266638,
    "previous_hash": "000371e99eb51d745c38925960c304a5c681f9cefc19c941fa72befd6d567a36",
    "total_difficulty": 2064958700115730
  },
  "header_height": 2268377,
  "network": {
    "height": 2268379,
    "num_inbound": 0,
    "num_outbound": 5,
    "total_difficulty": 2065383457733505
  },
  "protocol_version": 1000,
  "state": {
    "download_size": 0,
    "downloaded": 0,
    "processing_status": 0
  },
  "sync_status": "SYNCING_BLOCKS",
  "user_agent": "Grin++ 1.2.8"
}

{
  "chain": {
    "hash": "000226d54b1db6763bb26744cbfb4aa172d66c2697a57dcff04f5662001b4697",
    "height": 2268385,
    "previous_hash": "0002dce631821930aa8c051042b0919f281279d86ae846df1d1a7d58ed95dd4e",
    "total_difficulty": 2065384900184026
  },
  "header_height": 2268385,
  "network": {
    "height": 2268385,
    "num_inbound": 0,
    "num_outbound": 7,
    "total_difficulty": 2065384900184026
  },
  "protocol_version": 1000,
  "state": {
    "download_size": 0,
    "downloaded": 0,
    "processing_status": 0
  },
  "sync_status": "FULLY_SYNCED",
  "user_agent": "Grin++ 1.2.8"
}
"""


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
