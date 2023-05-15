from rich import print
from typing import Optional


from modules.api.owner.v3 import call_owner_rpc_v3


def open_wallet(name: str, password: str) -> dict:
    result = call_owner_rpc_v3("open_wallet", {"username": name, "password": password})
    print(result)
    return result


def create_wallet(
    name: str, password: str, mnemonic_length: int = 42, mnemonic: Optional[str] = None
) -> dict:
    result = call_owner_rpc_v3(
        "open_wallet",
        {
            "username": name,
            "password": password,
            "mnemonic_length": mnemonic_length,
            "mnemonic": mnemonic,
        },
    )
    print(result)
    return result
