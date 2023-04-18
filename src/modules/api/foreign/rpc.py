#!/usr/bin/env python3

from modules.api.foreign import _owner_foreign_rpc_call


def get_list_of_settings() -> dict:
    return _owner_foreign_rpc_call("get_config")
