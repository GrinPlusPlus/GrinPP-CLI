from modules.api.owner.v2 import call_owner_rpc_v2


def parse_node_status(status: dict) -> tuple[str, float]:
    """
    Parse status response in order to get a human-like messange and a percentage.

    Returns
    ------
    tuple[str, float]
        A tuple containing the huma-like message and percentage.
    """
    message = "Waiting for Peers"
    percentage = 0.0

    if status["sync_status"] == "no_sync":
        message = "Running"
        percentage = 100

    elif status["sync_status"] == "header_sync":
        message = "1/7 Syncing Headers"
        if status["sync_info"]["highest_height"] > 0:
            percentage = (
                status["sync_info"]["current_height"]
                * 100
                / status["sync_info"]["highest_height"]
            )

    elif status["sync_status"] == "txhashset_download":
        message = "2/7 Downloading Chain State"
        if status["sync_info"]["downloaded_size"] > 0:
            percentage = (
                status["sync_info"]["downloaded_size"]
                * 100
                / status["sync_info"]["total_size"]
            )
    elif status["sync_status"] == "syncing":
        message = "Preparing Chain State for Validation"

    elif status["sync_status"] == "txhashset_rangeproofs_validation":
        message = "3/7 Validating Chain State"
    elif status["sync_status"] == "txhashset_kernels_validation":
        message = "4/7 Validating Chain State"
    elif status["sync_status"] == "txhashset_kernels_validation":
        message = "4/7 Validating Chain State"

    elif status["sync_status"] == "txhashset_processing":
        message = "5/7 Validating Chain State"

    elif status["sync_status"] == "body_sync":
        message = "7/7 Syncing Blocks"
        if status["sync_info"]["highest_height"] > 0:
            percentage = (
                status["sync_info"]["current_height"]
                * 100
                / status["sync_info"]["highest_height"]
            )

    return message, percentage


def get_status() -> dict:
    """
    Get various information about the node, the network and the current sync status.

    Returns
    ------
    dict
        A dict containing protocol_version, user_agent, connections, tip and
        sync_status.
    """
    result = call_owner_rpc_v2("get_status")

    return result


def get_connected_peers() -> dict:
    """
    Retrieves a list of all connected peers.

    Returns
    ------
    dict
        A list containing peers.
    """
    result = call_owner_rpc_v2("get_connected_peers")
    return result
