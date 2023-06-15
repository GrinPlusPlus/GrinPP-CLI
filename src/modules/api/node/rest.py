#!/usr/bin/env python3

from modules.api import _is_node_running
from modules.api.node import _node_rest_call, _parse_status_response


def get_node_state() -> dict:
    return _node_rest_call("status")


def get_sync_state() -> tuple[str, float]:
    return _parse_status_response(get_node_state())


def get_node_connected_peers() -> list:
    peers: list = []
    peer: dict
    for peer in _node_rest_call("peers", "/connected"):
        peers.append(peer)
    return peers


def shutdown_node() -> bool:
    _node_rest_call("shutdown")
    return _is_node_running() == False
