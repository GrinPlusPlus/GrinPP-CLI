from rich import print

from modules.api.owner.v3 import call_owner_rpc_v3


def open_wallet_by_name(name: str, password: str) -> dict:
    result = call_owner_rpc_v3("open_wallet", {"username": name, "password": password})
    print(result)
    return result
