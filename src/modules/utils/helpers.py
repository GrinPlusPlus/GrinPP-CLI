#!/usr/bin/env python3

import os
import signal
from pathlib import Path

import psutil
import requests
from cryptography.fernet import Fernet
from pynostr.key import PrivateKey

from modules.utils.kdf import derive_key, encode_derived_key


def find_processes_by_name(name: str) -> list[psutil.Process]:
    "Return a list of processes matching 'name'."
    ls: list[psutil.Process] = []
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        if (
            name == p.info["name"]
            or p.info["exe"]
            and os.path.basename(p.info["exe"]) == name
            or p.info["cmdline"]
            and p.info["cmdline"][0] == name
        ):
            ls.append(p)
    return ls


def kill_proc_tree(
    pid: int,
    sig: signal.Signals = signal.SIGTERM,
    include_parent: bool = True,
    timeout: float = None,
    on_terminate: callable = None,
) -> tuple[list[psutil.Process], list[psutil.Process]]:
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
    return (gone, alive)


def save_wallet_session(
    wallet: str,
    session_token: str,
    password: str,
) -> bool:
    """Save the the session token and the nostr public key encrypted.

    Returns a boolean value indicating whether the session was saved or not.
    """

    passphrase: str = f"{wallet}{password}"
    key: bytes = derive_key(passphrase=passphrase.encode(), generate_salt=True)
    encoded_key = encode_derived_key(key)

    token_path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.token"
    )
    with open(token_path, "wb+") as file:
        file.write(Fernet(encoded_key).encrypt(session_token.encode()))

    return token_path.exists()


def get_wallet_session(wallet: str, password: str) -> str:
    """Return a string containing the Session token."""
    session_token: str = ""
    encrypted_session_token: bytes = bytes()

    passphrase: str = f"{wallet}{password}"
    key: bytes = derive_key(passphrase.encode(), generate_salt=False)
    encoded_key: bytes = encode_derived_key(key)

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


def save_wallet_nostr_key(
    wallet: str,
    slatepack_address: str,
    password: str,
) -> bool:
    """Save the the encrypted nostr public key .

    Returns a boolean value indicating whether the key was created or not.
    """
    nostr_key: PrivateKey = None
    raw_key: bytes = None

    nostr_key, raw_key = get_nostr_private_key(
        slatepack_address=slatepack_address, password=password
    )

    nostr_key_path: Path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.nostr"
    )

    with open(nostr_key_path, "wb+") as file:
        file.write(
            Fernet(encode_derived_key(raw_key)).encrypt(
                nostr_key.public_key.bech32().encode()
            )
        )

    return nostr_key_path.exists()


def get_wallet_nostr_public_key(
    wallet: str, slatepack_address: str, password: str
) -> str:
    """Return a string containing the nostr Public key."""
    nostr_public_key: str = ""

    passphrase: str = f"{slatepack_address}{password}"
    key: bytes = derive_key(passphrase=passphrase.encode(), generate_salt=True)

    encrypted_nostr_key: bytes = bytes()
    nostr_key_path: Path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.nostr"
    )
    with open(nostr_key_path, "rb") as file:
        encrypted_nostr_key = file.read()
    try:
        nostr_public_key = (
            Fernet(encode_derived_key(key)).decrypt(encrypted_nostr_key).decode()
        )
    except:
        raise Exception("Invalid password.")

    return nostr_public_key


def get_nostr_private_key(
    slatepack_address: str, password: str
) -> tuple[PrivateKey, bytes]:
    """Return a tuple: Nostr Private Key and raw bytes"""
    passphrase: str = f"{slatepack_address}{password}"
    key: bytes = derive_key(passphrase=passphrase.encode(), generate_salt=True)
    return PrivateKey(raw_secret=key), key


def check_wallet_reachability(
    slatepack_address: str, api_url: str = "http://192.227.214.130/"
) -> bool:
    try:
        return (
            requests.post(
                url=api_url,
                data={
                    "wallet": slatepack_address,
                },
            ).status_code
            == 200
        )
    except requests.exceptions.ConnectionError:
        error = "Unable to connect to the GrinChck API"
        raise Exception(error)
