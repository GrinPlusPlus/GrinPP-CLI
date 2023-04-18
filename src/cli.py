#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from apps.misc import app as misc_app
from apps.node import app as node_app
from apps.transaction import app as transaction_app
from apps.wallet import app as wallet_app

__appname__ = "Grin++ CLI"
__version__ = "0.2.0"


Path(Path.home().joinpath(os.getenv("GRINPP_CLI_DATA_PATH", ".grinplusplus"))).mkdir(
    parents=True, exist_ok=True
)


def version_callback(value: bool):
    if value:
        typer.echo(f"{__appname__} v{__version__}")
        raise typer.Exit()


def main(
    debug: bool = typer.Option(
        default=False,
        help="Enable the verbose mode for troubleshooting purposes.",
    ),
    json: bool = typer.Option(
        default=False,
        help="Return json instead",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Return current version.",
    ),
):
    """
    Grin++: Fast, Private and Secure Grin Wallet.

    Grin is a lightweight implementation of the Mimblewimble protocol. The main goals and features of the Grin project are: Privacy, Scalability, Simplicity, Simple Cryptography and Decentralization. Grin wants to be usable by everyone, regardless of borders, culture, capabilities or access. To learn more about Grin, visit GRIN.MW.
    """
    if debug:
        state["verbose"] = True
    if json:
        state["json"] = True


cli = typer.Typer(
    callback=main,
    no_args_is_help=True,
    epilog="If you need support, please join the Grin++ group on Telegram: https://t.me/GrinPP",
)
state = {"verbose": False, "json": False}
console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red")

cli.add_typer(
    misc_app.app,
    name="misc",
    no_args_is_help=True,
    help="Miscellaneous cool things! Give it a try (งツ)ว",
)

cli.add_typer(
    wallet_app.app,
    name="wallet",
    no_args_is_help=True,
    help="Wallet management commands. Use this set of commands to create, open and manage your wallets.",
)

cli.add_typer(
    node_app.app,
    name="node",
    no_args_is_help=True,
    help="Manage the status of the local Grin++ node. Launch, stop, (re)Sync, and many more.",
)

cli.add_typer(
    transaction_app.app,
    name="transaction",
    no_args_is_help=True,
    help="Execute all actions regarding transactions. These actions require to be executed upon an open wallet.",
)


if __name__ == "__main__":
    cli()
