#!/usr/bin/env python3

from typing import Literal

from modules.api.owner import _filter_transactions_by_status, _owner_wallet_rpc_call


def get_list_of_wallets() -> list[str]:
    wallets: list[str] = []
    wallet: str
    for wallet in _owner_wallet_rpc_call("list_wallets", {}):
        wallets.append(wallet)
    return wallets


def open_wallet_by_name(name: str, password: str):
    return _owner_wallet_rpc_call("login", {"username": name, "password": password})


def get_wallet_transactions(
    session_token: str,
    status: Literal["all", "coinbase", "sent", "pending", "received", "canceled"],
) -> list:
    transactions: list = _owner_wallet_rpc_call(
        "list_txs", {"session_token": session_token}
    )["txs"]
    return list(_filter_transactions_by_status(transactions, status))


def close_wallet_by_name(session_token: str) -> None:
    _owner_wallet_rpc_call("logout", {"session_token": session_token})
    return


def get_wallet_balance(session_token: str):
    return _owner_wallet_rpc_call("get_balance", {"session_token": session_token})


def get_wallet_slatepack_address(session_token: str) -> str:
    response: dict = _owner_wallet_rpc_call(
        "get_slatepack_address", {"session_token": session_token}
    )
    return response["slatepack"]


def get_wallet_seed(wallet: str, password: str) -> str:
    response: dict = _owner_wallet_rpc_call(
        "get_wallet_seed", {"username": wallet, "password": password}
    )
    return response["wallet_seed"]


def delete_wallet_by_name(wallet: str, password: str) -> bool:
    response: dict = _owner_wallet_rpc_call(
        "delete_wallet", {"username": wallet, "password": password}
    )
    return response["status"] == "SUCCESS"


def create_wallet(wallet: str, password: str, words: int) -> dict:
    return _owner_wallet_rpc_call(
        "create_wallet",
        {
            "username": wallet,
            "password": password,
            "num_seed_words": words,
        },
    )


def estimate_transaction_fee(session_token: str, amount: float) -> dict:
    params: dict = {
        "session_token": session_token,
        "amount": amount * pow(10, 9),
        "fee_base": 500000,
        "change_outputs": 1,
        "selection_strategy": {"strategy": "SMALLEST"},
    }
    return _owner_wallet_rpc_call(
        "estimate_fee",
        params,
    )


def send_coins(
    session_token: str,
    amount: float,
    address: str = "",
) -> dict:
    params: dict = {
        "session_token": session_token,
        "address": address,
        "amount": amount * pow(10, 9),
        "fee_base": 500000,
        "change_outputs": 1,
        "selection_strategy": {"strategy": "SMALLEST", "inputs": []},
        "post_tx": {"method": "FLUFF"},
    }
    return _owner_wallet_rpc_call("send", params)


def cancel_transaction(session_token: str, id: int) -> dict:
    response: dict = _owner_wallet_rpc_call(
        "cancel_tx",
        {
            "session_token": session_token,
            "tx_id": id,
        },
    )
    return response["status"] == "SUCCESS"


def add_signature_to_transaction(session_token: str, slatepack: str) -> dict:
    response: dict = _owner_wallet_rpc_call(
        "finalize",
        {
            "session_token": session_token,
            "slatepack": slatepack.rstrip().strip(),
        },
    )
    return response["status"] == "FINALIZED"


def add_initial_signature(session_token: str, slatepack: str) -> dict:
    return _owner_wallet_rpc_call(
        "receive",
        {
            "session_token": session_token,
            "slatepack": slatepack.rstrip().strip(),
        },
    )


def broadcast_transaction(session_token: str, id: int) -> bool:
    response = _owner_wallet_rpc_call(
        "repost_tx",
        {"session_token": session_token, "tx_id": id, "method": "FLUFF"},
    )
    if "status" in response:
        return response["status"] != "FAILED"
    return True


def get_transaction_details(session_token: str, id: int) -> dict:
    transactions = _owner_wallet_rpc_call("list_txs", {"session_token": session_token})

    return next((x for x in transactions["txs"] if x["id"] == id))


def restore_wallet(wallet: str, password: str, seed: str) -> dict:
    return _owner_wallet_rpc_call(
        "restore_wallet",
        {
            "username": wallet,
            "password": password,
            "wallet_seed": seed.strip(),
        },
    )
