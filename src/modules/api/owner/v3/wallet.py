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
