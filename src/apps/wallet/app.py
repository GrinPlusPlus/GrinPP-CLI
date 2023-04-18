#!/usr/bin/env python3

import json

import typer
from rich import box
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from modules.api.owner.rpc import (
    close_wallet_by_name,
    create_wallet,
    delete_wallet_by_name,
    get_list_of_wallets,
    get_wallet_balance,
    get_wallet_seed,
    get_wallet_slatepack_address,
    open_wallet_by_name,
    restore_wallet,
)
from modules.utils.helpers import (
    get_wallet_nostr_public_key,
    get_wallet_session,
    save_wallet_nostr_key,
    save_wallet_session,
)

app = typer.Typer()
console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red")


@app.command(name="open")
def wallet_open(
    wallet: str = typer.Option(
        ..., help="Name of the wallet you want to open", prompt=True
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
):
    """
    Open a Wallet, then start the Tor Listener automatically.
    """

    try:
        result = open_wallet_by_name(wallet, password)
        console.print(f"Wallet [bold]{wallet}[/bold] opened ✔")
        console.print(f"Tor Listener for wallet [bold]{wallet}[/bold] running ✔")
        session_saved = save_wallet_session(
            wallet=wallet,
            session_token=result["session_token"],
            password=password,
        )
        if not session_saved:
            error_console.print(f"Error: Unable to save session information ✗")
        else:
            console.print(f"Session information created ✔")

        nostr_key_saved = save_wallet_nostr_key(
            wallet=wallet,
            slatepack_address=result["slatepack_address"],
            password=password,
        )

        if not nostr_key_saved:
            error_console.print(f"Error: Unable to generate Nostr key ✗")
        else:
            console.print(f"Nostr root key loaded ✔")

        console.print(
            f"Slatepack Address: [green3]{result['slatepack_address']}[/green3] "
        )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="close")
def wallet_close(
    wallet: str = typer.Option(
        ..., help="Name of the wallet you want to close", prompt=True
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
):
    """
    Close a running Wallet and stop the Tor Listener.
    """

    try:
        session_token: str = get_wallet_session(wallet=wallet, password=password)
        with console.status("closing walet..."):
            close_wallet_by_name(session_token)
        console.print(
            f"Wallet [bold]{wallet}[/bold] closed, and Tor Listener [bold]stopped[/bold] successfully ✔"
        )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="create")
def wallet_creation(
    name: str = typer.Option(
        ..., help="Name of the wallet you want to create", prompt=True
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
    words: int = typer.Option(24, help="Number of words for the mnemonic seed"),
):
    """
    Create a new Wallet, open it and start the Tor Listener.
    """

    try:
        wallet = create_wallet(wallet=name, password=password, words=words)
        console.print(f"Wallet [bold]{wallet}[/bold] created ✔")

        session_saved = save_wallet_session(
            wallet=name,
            session_token=wallet["session_token"],
            password=password,
        )
        console.print(f"Tor Listener for wallet [bold]{wallet}[/bold] running ✔")

        if not session_saved:
            raise Exception("An error occurred while saving session information")

        nostr_key_saved = save_wallet_nostr_key(
            wallet=name,
            slatepack_address=wallet["slatepack_address"],
            password=password,
        )

        if not nostr_key_saved:
            error_console.print(f"Error: {err} ✗")
        else:
            console.print(f"Nostr root key loaded ✔")

        console.print(f"Wallet seed phrase: [bold]{wallet['wallet_seed']}[/bold] ✇")
        console.print(
            f"Slatepack Address: [green3]{wallet['slatepack_address']}[/green3] "
        )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="recover")
def wallet_restore(
    name: str = typer.Option(
        ..., help="Name for the wallet you want to recover", prompt=True
    ),
    seed: str = typer.Option(..., help="Seed phrase", prompt=True),
    password: str = typer.Option(
        ...,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
):
    """
    Recover a Wallet using the seed phrase.
    """

    try:
        wallet = restore_wallet(wallet=name, password=password, seed=seed)
        console.print(f"Wallet [bold]{wallet}[/bold] recovered ✔")
        session_saved = save_wallet_session(
            wallet=name,
            session_token=wallet["session_token"],
            password=password,
        )
        if not session_saved:
            error_console.print(f"Error: {err} ✗")
        else:
            console.print(f"Session information created ✔")

        nostr_key_saved = save_wallet_nostr_key(
            wallet=name,
            slatepack_address=wallet["slatepack_address"],
            password=password,
        )

        if not nostr_key_saved:
            error_console.print(f"Error: {err} ✗")
        else:
            console.print(f"Nostr root key loaded ✔")

        console.print(
            f"Slatepack Address: [green3]{wallet['slatepack_address']}[/green3] "
        )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="delete")
def wallet_removal(
    name: str = typer.Option(
        ..., help="Name of the wallet you want to delete", prompt=True
    ),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Wallet password."
    ),
):
    """
    Delete a Wallet.
    """

    if Confirm.ask("Are you sure you want to delete the wallet?", default=False):
        try:
            seed = get_wallet_seed(wallet=name, password=password)
            console.print(
                f"Wallet seed phrase: [bold italic]{seed}[/bold italic]", style=""
            )

            delete_wallet_by_name(wallet=name, password=password)

            console.print(f"Wallet [bold]{name}[/bold] deleted")
        except Exception as err:
            error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
            raise typer.Abort()

    raise typer.Exit()


@app.command(name="backup")
def wallet_backup(
    wallet: str = typer.Option(..., help="Name of the wallet you want to backup."),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Wallet password."
    ),
):
    """
    Backup a Wallet.
    """

    try:
        seed = get_wallet_seed(wallet=wallet, password=password)
        console.print(f"wallet seed: [bold white]{seed}[/bold white]")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="list")
def list_wallets():
    """
    List the created Wallets.
    """
    data = json.loads("{}")

    try:
        data = get_list_of_wallets()
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    if data["wallets"]:
        table = Table(title="Wallets", box=box.HORIZONTALS, expand=True)
        table.add_column("")
        table.add_column("name")
        i = 1
        for wallet in data["wallets"]:
            table.add_row(
                f"{i}",
                f"[bold yellow]{wallet}",
            )
            i += 1

        console.print(table)
    else:
        console.print("No wallet found")

    raise typer.Exit()


@app.command(name="balance")
def wallet_balance(
    wallet: str = typer.Option(
        ..., help="Name of the wallet you want to check", prompt="Wallet name"
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
):
    """
    Get the balance of a running Wallet.
    """

    try:
        session_token = get_wallet_session(wallet=wallet, password=password)

        balance = get_wallet_balance(session_token)

        table = Table(
            title="Wallet's Balance",
            box=box.HORIZONTALS,
            show_footer=True,
            show_header=True,
            expand=True,
        )

        table.add_column("", "Total", justify="right")
        table.add_column(
            "amount ツ", f'{balance["total"] / pow(10, 9):10,.9f} ', justify="right"
        )
        table.add_row(
            "Spendable:",
            f'[green3]{balance["spendable"] / pow(10, 9):10,.9f}',
            style="bold",
        )
        table.add_row(
            "Immature:", f'[dark_orange3]{balance["immature"] / pow(10, 9):10,.9f}'
        )
        table.add_row(
            "Unconfirmed:", f'[gold1]{balance["unconfirmed"] / pow(10, 9):10,.9f}'
        )
        table.add_row(
            "Locked:", f'[bright_black]{balance["locked"] / pow(10, 9):10,.9f}'
        )

        console.print(table)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="address")
def wallet_address(
    wallet: str = typer.Option(
        ..., help="Name of the opened wallet you want to query", prompt="Wallet"
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        help="Wallet password.",
    ),
    nostr: bool = typer.Option(
        False, help="Return the nostr Public Key associated with the current address"
    ),
    check: bool = typer.Option(False, help="Check if address are reachable via Tor"),
):
    """
    Get the Slatepack Address of a running Wallet.
    """

    try:
        session_token = get_wallet_session(wallet=wallet, password=password)

        slatepack_address = get_wallet_slatepack_address(session_token)

        console.print(f"Slatepack Address: [green3]{slatepack_address}[/green3] ")

        if nostr:
            nostr_public_key = get_wallet_nostr_public_key(
                wallet=wallet,
                slatepack_address=slatepack_address,
                password=password,
            )
            if nostr_public_key:
                console.print(
                    f"Nostr' Public Key: [dark_orange3]{nostr_public_key}[/dark_orange3] (∩｀-´)⊃━☆ﾟ.*･｡ﾟ"
                )
            else:
                error_console.print("No nostr key was found for this address")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()
