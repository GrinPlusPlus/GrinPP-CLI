#!/usr/bin/env python3
import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(passphrase, generate_salt=False):
    salt = _SaltManager(generate_salt)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.get(),
        iterations=1000,
        backend=default_backend(),
    )
    return kdf.derive(passphrase)


def encode_derived_key(derived_key: bytes):
    return base64.urlsafe_b64encode(derived_key)


class _SaltManager(object):
    def __init__(self, generate, path=".salt"):
        self.generate = generate
        self.path = path

    def get(self):
        if self.generate:
            return self._generate_and_store()
        return self._read()

    def _generate_and_store(self):
        if not os.path.exists(self.path):
            salt = os.urandom(16)
            with open(self.path, "xb") as f:
                f.write(salt)
            return salt
        return self._read()

    def _read(self):
        with open(self.path, "rb+") as f:
            return f.read()
