#!/usr/bin/env python3

import typer
from rich import box
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from modules import nostr

from modules.utils import grinchck
from modules.wallet import session
from modules.api.owner.v3.wallet import (
    delete_wallet,
    get_mnemonic,
    get_top_level_directory,
    list_wallets,
    open_wallet,
    close_wallet,
    create_wallet,
    restore_wallet,
    retrieve_outputs,
    retrieve_summary_info,
    get_slatepack_address,
)

app = typer.Typer()
console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red", width=125)


@app.command(name="open")
def open(
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
        response = open_wallet(wallet=wallet, password=password)
        console.print(f"Wallet [bold]{wallet}[/bold] opened ✔")

        if not session.store(
            wallet=wallet,
            token=response["session_token"],
            password=password,
        ):
            close_wallet(response["session_token"])
            raise Exception("Unable to save session information ✗")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="close")
def close(
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
        session_token: str = session.token(wallet=wallet, password=password)
        with console.status("closing walet..."):
            close_wallet(session_token)
        console.print(f"Wallet [bold]{wallet}[/bold] closed successfully ✔")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="create")
def create(
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
        response = create_wallet(wallet=name, password=password, mnemonic_length=words)
        console.print(f"Wallet [bold]{name}[/bold] created ✔")
        console.print(f"Wallet seed phrase: [bold]{response['wallet_seed']}[/bold] ✇")

        if not session.store(
            wallet=name,
            token=response["session_token"],
            password=password,
        ):
            close_wallet(response["session_token"])
            raise Exception("Unable to save session information ✗")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="recover")
def recover(
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
        response = restore_wallet(wallet=name, password=password, mnemonic=seed)
        console.print(f"Wallet [bold]{name}[/bold] recovered ✔")

        if not session.store(
            wallet=name,
            token=response["session_token"],
            password=password,
        ):
            raise Exception("Unable to save session information ✗")

        console.print(f"Session information created ✔")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="delete")
def delete(
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
            seed = get_mnemonic(wallet=name, password=password)
            console.print(
                f"Wallet seed phrase: [bold italic]{seed}[/bold italic]", style=""
            )

            delete_wallet(wallet=name, password=password)

            console.print(f"Wallet [bold]{name}[/bold] deleted")
        except Exception as err:
            error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
            raise typer.Abort()

    raise typer.Exit()


@app.command(name="seed")
def backup(
    wallet: str = typer.Option(..., help="Name of the wallet you want to backup."),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Wallet password."
    ),
):
    """
    Export the Seed the Wallet.
    """

    try:
        seed = get_mnemonic(wallet=wallet, password=password)
        console.print(f"Wallet seed phrase: [bold white]{seed}[/bold white]")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="list")
def wallet_list():
    """
    List the created Wallets.
    """

    try:
        wallets = list_wallets()
        if wallets:
            table = Table(title="Wallets", box=box.HORIZONTALS, expand=True)
            table.add_column("")
            table.add_column("name")
            i = 1
            for wallet in wallets:
                table.add_row(
                    f"{i}",
                    f"[bold yellow]{wallet}",
                )
                i += 1

            console.print(table)
        else:
            console.print("No wallet found")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="balance")
def get_balance(
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
        token = session.token(wallet=wallet, password=password)

        balance = retrieve_summary_info(token)

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
    test: bool = typer.Option(
        False, help="Check if wallet address is reachable via Tor"
    ),
    npub: bool = typer.Option(False, help="Print the Nostr Public Key"),
):
    """
    Get the Slatepack Address of a running Wallet.
    """

    try:
        session_token = session.token(wallet=wallet, password=password)
        address = get_slatepack_address(session_token)
        console.print(f"Slatepack Address: [green3]{address}[/green3]")

        if test:
            reachable = grinchck.connect(
                slatepack_address=address["slatepack"],
                api_url="http://192.227.214.130/",
            )
            if reachable:
                console.print(
                    f"Address [green3]{address}[/green3] is reachable via the Tor Network <(^_^)>"
                )
            else:
                error_console.print(
                    f"Addres [dark_orange]{address}[/dark_orange] is not reachable the Tor Network \_(-_-)_/"
                )
        if npub:
            wallet_raw_secret = nostr.generate_raw_secret(
                wallet=wallet, address=address["slatepack"], password=password
            )
            nostr_private_key = nostr.retrieve_private_key(
                wallet=wallet, raw_secret=wallet_raw_secret
            )
            console.print(
                f"Nostr' Public Key: [dark_orange3]{nostr_private_key.public_key}[/dark_orange3] (∩｀-´)⊃━☆ﾟ.*･｡ﾟ"
            )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="outputs")
def list_outputs(
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
        token = session.token(wallet=wallet, password=password)

        outputs = retrieve_outputs(token)

        table = Table(
            title="Wallet's Outputs",
            box=box.HORIZONTALS,
            show_footer=True,
            show_header=True,
            expand=True,
        )
        table = Table(title="", box=box.HORIZONTALS, expand=True)
        table.add_column("amount ツ", justify="right", width=15)
        table.add_column("commitment", justify="center")
        table.add_column("status", justify="center", width=10)
        table.add_column("tx_id", justify="center")
        table.add_column("explorer", justify="center")

        for output in outputs:
            amount = output["amount"] / pow(10, 9)
            link = f"[link=https://grinexplorer.net/output/{output['commitment']}]Open[/link]"
            table.add_row(
                f"{amount:10,.9f}",
                f"{output['commitment']}",
                f"{output['status']}",
                f"{output['transaction_id']}",
                link,
            )
        console.print(table)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="directory")
def get_directory(
    wallet: str = typer.Option(
        ..., help="Name of the wallet you want query", prompt="Wallet name"
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
):
    """
    Get the information of a transaction using the Transaction Id.
    """

    try:
        session_token = session.token(wallet=wallet, password=password)
        folder = get_top_level_directory(session_token=session_token)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    console.print(
        f"*[italic]Slate exported to path: [yellow1]{folder}[yellow1]\n",
    )
    raise typer.Exit()
