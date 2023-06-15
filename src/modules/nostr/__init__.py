import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from pynostr.key import PrivateKey

from modules.utils.kdf import derive_key, encode_key


def _derive_passphrase(password: str):
    """
    Derive a key using a passphrase. The method will try to get an already stored `salt` or generate a new one if necessary.

    Parameters
    ----------
    password : str
        Password of the wallet.

    Returns
    -------
    bytes
        Raw bytes of the derived key.
    """
    return derive_key(passphrase=password.encode())


def _generate_private_key(nsec: Optional[str] = None) -> PrivateKey:
    """
    Generates a Nostr Private Key. It will use an nsec if passed as a parameter.

    Parameters
    ----------
    nsec : str
        An already generate nsec. It will create a completely new private if nsec is
        None.

    Returns
    -------
    PrivateKey
        A Nostr Private Key.
    """
    if nsec:
        return PrivateKey.from_nsec(nsec=nsec)
    return PrivateKey()


def _store_private_key(raw_secret: bytes, key_path: Path) -> PrivateKey:
    """
    Save a Nostr Privat Key inside `key_path`. The content is encrypted using
    `raw_secret`.

    Parameters
    ----------
    raw_secret: bytes
        Secret key used to decrypt/encrypt the line with the nsec.
    key_path : Path
        Walle name. This is uses to name the file like: `[wallet].nostr`.

    Returns
    ------
    PrivateKey
        A Nostr Private Key.
    """
    private_key = _generate_private_key()
    with open(key_path, "wb+") as file:
        file.write(
            Fernet(encode_key(raw_secret)).encrypt(private_key.bech32().encode())
        )
    if key_path.exists():
        return private_key
    raise Exception("Unable to store generated Nostr Private Key")


def generate_raw_secret(wallet: str, address: str, password: str) -> bytes:
    """
    Get a raw secret based on wallet address to encrypt/decrypt the file containing the
    nsec.

    Parameters
    ----------
    wallet : str
        Name of the wallet.
    address : str
        Slatepack Address of the wallet.
    password : str
        Password of the wallet.

    Returns
    -------
    bytes
        Raw bytes of the derived key.
    """
    """
    Returns a tuple: Nostr Private Key and raw bytes
    """
    return _derive_passphrase(f"{wallet}{address}{password}")


def retrieve_private_key(wallet: str, raw_secret: bytes) -> PrivateKey:
    """
    Returns the corresponding Nostr Private Key of a opened wallet. This will create a
    new Private Key in case the contents of the file containing the nsec cannot be
    decrypted.

    Parameters
    ----------
    wallet : str
        Walle name. This is uses to name the file like: `[wallet].nostr`.
    raw_secret: bytes
        Secret key used to decrypt/encrypt the line with the nsec.

    Returns
    ------
    PrivateKey
        A Nostr Private Key.
    """

    key_path: Path = Path.home().joinpath(
        os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"), f"{wallet}.nostr"
    )
    if key_path.exists():
        file = open(key_path, "rb")
        nostr_key = file.read()
        file.close()
        try:
            nsec = Fernet(encode_key(raw_secret)).decrypt(nostr_key).decode()
            return _generate_private_key(nsec=nsec)
        except:
            return _store_private_key(raw_secret, key_path)

    return _store_private_key(raw_secret, key_path)
