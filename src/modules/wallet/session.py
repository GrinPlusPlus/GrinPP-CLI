"""
After opening a wallet, a session token is needed to communicate with the Grin API. The token is used to identify the wallet. This module contains what is needed to store the token information.
"""
import os
from pathlib import Path

from cryptography.fernet import Fernet

from modules.utils.kdf import derive_key, encode_key


def store(
    wallet: str,
    token: str,
    password: str,
) -> bool:
    """
    Saves the session token locally. The token is encrypted before saving.

    Parameters
    ----------
    wallet : str
        Walle name. This is uses to name the file like: `[wallet].token`.
    token : str
        Session token used to communicate with the Grin API.
    password: str
        Password used to encrypt the session token.

    Returns
    ------
    bool
        It would be True if the file is correctly stored.
    """

    passphrase: str = f"{wallet}{password}"
    key: bytes = derive_key(passphrase=passphrase.encode())
    encoded_key = encode_key(key)

    token_path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.token"
    )
    with open(token_path, "wb+") as file:
        file.write(Fernet(encoded_key).encrypt(token.encode()))

    return token_path.exists()


def token(wallet: str, password: str) -> str:
    """
    Returns the corresponding session token of an opened wallet.

    Parameters
    ----------
    wallet : str
        Walle name. This is uses to name the file like: `[wallet].token`.
    password: str
        Password used to encrypt the session token.

    Returns
    ------
    str
        A string containing the session token.
    """
    session_token: str = ""
    encrypted_session_token: bytes = bytes()

    passphrase: str = f"{wallet}{password}"
    key: bytes = derive_key(passphrase.encode())
    encoded_key: bytes = encode_key(key)

    token_path: Path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.token"
    )
    with open(token_path, "rb") as file:
        encrypted_session_token = file.read()

    try:
        session_token = Fernet(encoded_key).decrypt(encrypted_session_token).decode()
    except:
        raise Exception("Invalid password.")

    return session_token
