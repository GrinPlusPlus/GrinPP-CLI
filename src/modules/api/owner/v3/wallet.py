from modules.api.owner.v3 import call_owner_rpc_v3 as call
from modules.api.owner.v3.helpers import filter_transactions


def list_wallets() -> list[str]:
    wallets: list[str] = []
    for wallet in call("list_wallets", {}):
        wallets.append(wallet)
    return wallets


def open_wallet(
    wallet: str,
    password: str,
) -> dict:
    return call("open_wallet", {"name": wallet, "password": password})


def close_wallet(session_token: str) -> dict:
    return call("close_wallet", {"session_token": session_token})


def create_wallet(wallet: str, password: str, mnemonic_length: int = 24) -> dict:
    return call(
        "create_wallet",
        {
            "username": wallet,
            "password": password,
            "mnemonic_length": mnemonic_length,
        },
    )


def get_mnemonic(
    wallet: str,
    password: str,
) -> dict:
    return call("get_mnemonic", {"name": wallet, "password": password})


def delete_wallet(
    wallet: str,
    password: str,
) -> dict:
    return call("delete_wallet", {"name": wallet, "password": password})


def restore_wallet(wallet: str, password: str, mnemonic: str) -> dict:
    return call(
        "create_wallet",
        {
            "username": wallet,
            "password": password,
            "mnemonic": mnemonic,
        },
    )


def retrieve_summary_info(session_token: str) -> dict:
    return call("retrieve_summary_info", {"session_token": session_token})


def get_slatepack_address(session_token: str) -> dict:
    return call("get_slatepack_address", {"session_token": session_token})


def retrieve_txs(session_token: str, status: str) -> list:
    result = call("retrieve_txs", {"session_token": session_token})
    return filter_transactions(result[1], status)


def get_stored_tx(session_token: str, slate_id: str) -> dict:
    return call("get_stored_tx", {"session_token": session_token, "slate_id": slate_id})


def slate_from_slatepack_message(session_token: str) -> dict:
    return call("slate_from_slatepack_message", {"session_token": session_token})


def get_tx_details(session_token: str, tx_id: int) -> dict:
    return call("get_tx_details", {"session_token": session_token, "tx_id": tx_id})


def retrieve_outputs(session_token: str) -> dict:
    return call("retrieve_outputs", {"session_token": session_token})


def get_top_level_directory(session_token: str) -> dict:
    return call("get_top_level_directory", {"session_token": session_token})


def post_tx(session_token: str, tx_id: int) -> dict:
    return call(
        "post_tx", {"session_token": session_token, "tx_id": tx_id, "method": "FLUFF"}
    )


def estimate_fee(
    session_token: str,
    amount: float = -1,
) -> dict:
    params: dict = {
        "session_token": session_token,
        "fee_base": 500000,
        "selection_strategy": {"strategy": "SMALLEST", "inputs": []},
    }
    if amount > 0:
        params["amount"] = str(amount * pow(10, 9))

    return call("estimate_fee", params)


def send_tx(
    session_token: str,
    amount: float = -1,
    address: str = "",
) -> dict:
    params: dict = {
        "session_token": session_token,
        "address": address,
        "fee_base": 500000,
        "change_outputs": 1,
        "selection_strategy": {"strategy": "SMALLEST", "inputs": []},
        "post_tx": {"method": "FLUFF"},
    }
    if amount > 0:
        params["amount"] = str(amount * pow(10, 9))

    return call("send", params)


def cancel_tx(session_token: str, tx_id: int) -> dict:
    return call("cancel_tx", {"session_token": session_token, "tx_id": tx_id})


def receive_tx(session_token: str, slatepack: str) -> dict:
    return call("receive_tx", {"session_token": session_token, "slatepack": slatepack})


def decode_slatepack(session_token: str, message: str) -> dict:
    return call(
        "decode_slatepack_message", {"session_token": session_token, "message": message}
    )


def finalize_tx(session_token: str, slatepack: str) -> dict:
    return call("finalize_tx", {"session_token": session_token, "slatepack": slatepack})
