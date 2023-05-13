from enum import Enum

import psutil

from modules.utils.processes import find


class TransactionsFilterOptions(str, Enum):
    coinbase = "coinbase"
    sent = "sent"
    pending = "pending"
    received = "received"
    canceled = "canceled"
    all = "all"


def _get_process_status_error() -> str:
    if not _is_node_running():
        error = "Grin node is not running"
    return "Unable to connect to the node"


def _is_node_running() -> bool:
    node_process_name = "GrinNode"
    if psutil.WINDOWS:
        node_process_name = "GrinNode.exe"

    return len(find(node_process_name)) > 0
