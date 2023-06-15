"""
Key derivation functions derive bytes suitable for cryptographic operations from passwords or other data sources using a pseudo-random function (PRF).
"""
import base64
import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class __SaltManager(object):
    """Salt Manager internal class."""

    def __init__(self):
        self.path = str(Path.home() / ".salt")

    def get(self):
        if not os.path.exists(self.path):
            return self._generate_and_store()
        return self._read()

    def _generate_and_store(self):
        salt = os.urandom(16)
        with open(self.path, "xb") as f:
            f.write(salt)
        return salt

    def _read(self):
        with open(self.path, "rb+") as f:
            return f.read()


def derive_key(passphrase) -> bytes:
    """
    Derive a key using a passphrase. The method will try to get an already stored `salt` or generate a new one if necessary.

    Parameters
    ----------
    passphrase : str
        Passphrase or password.

    Returns
    -------
    bytes
        Raw bytes of the derived key.
    """
    salt = __SaltManager()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.get(),
        iterations=1000,
        backend=default_backend(),
    )

    return kdf.derive(passphrase)


def encode_key(key: bytes):
    """
    Encode bytes using the URL- and filesystem-safe Base64 alphabet. Argument *derived_key* is a bytes-like object to encode.  The result is returned as a bytes object.

    Parameters
    ----------
    key : bytes
        Bytes of the key to encode.

    Returns
    -------
    bytes
        Raw bytes.
    """
    return base64.urlsafe_b64encode(key)
