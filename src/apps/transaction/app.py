#!/usr/bin/env python3

from datetime import datetime
from typing import Optional
from pathlib import Path

import psutil
import timeago
import typer
from rich import box
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from apps.transaction.nostr import transport
from modules.api import TransactionsFilterOptions
from modules.api.owner.rpc import (
    add_initial_signature,
    add_signature_to_transaction,
    broadcast_transaction,
    cancel_transaction,
    estimate_transaction_fee,
    get_transaction_details,
    get_wallet_transactions,
    send_coins,
)
from modules.api.owner.v3.wallet import (
    get_stored_tx,
    get_top_level_directory,
    get_tx_details,
    post_tx,
    retrieve_txs,
)
from modules.wallet import session

app = typer.Typer()

app.add_typer(
    transport.plugin,
    name="nostr",
    no_args_is_help=True,
    help="Nostr Transport Plugin for Grin transactions.",
)
console = Console(width=155, style="grey93")
error_console = Console(stderr=True, style="bright_red", width=155)


@app.command(name="list")
def list_wallet_transactions(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet from which you want to list transactions.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    status: TransactionsFilterOptions = typer.Option(
        default=TransactionsFilterOptions.pending.value,
        help="Status of the transactions you want to list.",
    ),
):
    """
    List the transactions of a running Wallet. Default status: Pending.
    """

    try:
        session_token = session.token(wallet=wallet, password=password)

        transactions = retrieve_txs(session_token, status.value)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    if len(transactions) == 0:
        console.print(f"No [bold]{status.value}[/bold] transaction were found.")
        raise typer.Exit()

    table = Table(title="", box=box.HORIZONTALS, expand=True)
    table.add_column("tx_id", justify="center", width=5)
    table.add_column("slate_id", justify="center", width=40)
    table.add_column("amount ツ", justify="right", width=15)
    table.add_column("fees ツ", justify="right", width=15)
    table.add_column("when?", justify="center", width=15)
    table.add_column("status", justify="center", width=10)
    table.add_column("height", justify="center")
    table.add_column("explorer", justify="center")

    style: str = ""
    status: str = ""
    for transaction in transactions:
        style = ""
        status = transaction["type"].lower()

        if status == "sent":
            style = "deep_sky_blue1"
        elif status == "received":
            style = "spring_green3"
        elif status == "canceled":
            style = "grey66"
        elif status == "sending (not finalized)":
            style = "royal_blue1"
            status = "unfinalized"
        elif status == "sending (finalized)":
            style = "cornflower_blue"
            status = "unconfirmed"
        elif status == "receiving (unconfirmed)":
            style = "cyan3"
            status = "unconfirmed"

        amount: float = 0
        fee = 0
        if "fee" in transaction:
            fee = transaction["fee"]

        if transaction["amount_debited"] - transaction["amount_credited"] > 0:
            amount = transaction["amount_credited"] - transaction["amount_debited"]
            if "fee" in transaction:
                amount = amount - fee
        else:
            amount = transaction["amount_debited"] - transaction["amount_credited"]
        amount = abs(amount)
        amount = amount / pow(10, 9)
        fee = fee / pow(10, 9)

        relative_date = timeago.format(
            datetime.fromtimestamp(transaction["creation_date_time"])
        )
        link: str = ""
        confirmed_height = "-"
        if "confirmed_height" in transaction:
            confirmed_height = transaction["confirmed_height"]
            link = f"[link=https://grinexplorer.net/output/{transaction['outputs'][0]['commitment']}]View in Explorer[/link]"

        table.add_row(
            f"{transaction['id']}",
            f"{transaction.get('slate_id', '')}",
            f"{amount:10,.9f}",
            f"{fee:10,.9f}" if fee > 0 else "-",
            f"{relative_date}",
            status,
            f"{confirmed_height}",
            link,
            style=style,
        )
    console.print(table)

    raise typer.Exit()


@app.command(name="send")
def send_grin(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet from which you wish to send the coins.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    amount: float = typer.Option(
        ..., help="Amount of ツ you want to send.", prompt="Amount of ツ"
    ),
    address: Optional[str] = typer.Option(
        "", help="Slatepack Address where you want to send the ツ"
    ),
    auto: Optional[bool] = typer.Option(
        False, help="Auto answer 'Yes' to all confirmations"
    ),
):
    """
    Send ツ to someone
    """

    session_token: str
    fee: float

    try:
        session_token = session.token(wallet=wallet, password=password)
        fee = float(
            estimate_transaction_fee(session_token=session_token, amount=amount)["fee"]
        ) / pow(10, 9)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    table: Table = Table(
        title="Transaction details", box=box.HORIZONTALS, expand=True, show_header=False
    )
    table.add_column("", justify="right", style="bold")
    table.add_column("", justify="left")
    table.add_row("wallet:", f"{wallet}")
    table.add_row("amount:", f"{amount:10,.9f} ツ")
    table.add_row("fee:", f"{fee:10.9f} ツ")
    if address:
        table.add_row("receiver:", f"{address}")

    console.print(table)
    console.print("")
    proceed: bool = False
    if auto:
        proceed = True
    else:
        proceed = Confirm.ask(
            "Are you sure you want to create this transaction?", default=False
        )
    if proceed:
        sent: bool = False
        slatepack: str = ""
        try:
            session_token = session.token(wallet=wallet, password=password)
            with console.status("Building transaction..."):
                transaction = send_coins(
                    session_token=session_token, amount=amount, address=address
                )
            slatepack = transaction["slatepack"]
            if transaction["status"] == "FINALIZED":
                sent = True
        except Exception as err:
            error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
            raise typer.Abort()

        if sent:
            console.print(f"Transaction built with {address} via Tor successfully ✔")
        elif not sent:
            error_console.print(f"Unable to build transaction with {address} via Tor ✗")

            console.print("\nPlease share the next Slatepack with the recipient:")
            console.print(
                f"\n[yellow1]{slatepack.strip().rstrip()}[yellow1]\n",
            )
            console.print(
                "*** Ask the recipient to add his signature by receiving this slatepack.",
                style="italic",
            )
            console.print(
                "Then execute the [bold]finalize[/bold] command and insert the signed Slatepack by him/she. ***",
                style="italic",
            )

    raise typer.Exit()


@app.command(name="cancel")
def transaction_cancelation(
    wallet: str = typer.Option(
        ..., help="Name of the wallet from which you wish to cancel the transaction."
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    id: int = typer.Option(
        ...,
        help="Id of the transaction you want to be canceled.",
        prompt="Transaction Id",
    ),
):
    """
    Cancel a transaction using the Transaction Id.
    """

    try:
        session_token = session.token(wallet=wallet, password=password)

        if cancel_transaction(session_token=session_token, id=id):
            console.print("Transaction [bold]canceled[/bold] successfully ✔")
        else:
            error_console.print("Unable to cancel the transaction ✗")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="finalize")
def transaction_finalization(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet from which you wish to finalize the transaction.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
):
    """
    Finalize an unfinalized transaction.
    """

    try:
        token = session.token(wallet=wallet, password=password)
        if not psutil.WINDOWS:
            import readline
        slatepack: str = console.input("Please, insert the Slatepack down below:\n")
        if add_signature_to_transaction(session_token=token, slatepack=slatepack):
            console.print("Transaction [bold]finalized[/bold] successfully ✔")
        else:
            error_console.print("Unable to finalized the transaction ✗")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="receive")
def transaction_receive(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet where you want to receive the coins.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
):
    """
    Receive a transaction using Slatepack Messsage
    """

    try:
        session_token = session.token(wallet=wallet, password=password)
        if not psutil.WINDOWS:
            import readline
        slatepack = console.input("Paste the Slatepack down below:\n")

        if len(slatepack.strip().rstrip()) == 0:
            raise Exception("Empty Slatepack")

        signed_slatepack = add_initial_signature(
            session_token=session_token, slatepack=slatepack
        )

        console.print("\nPlease share the next Slatepack with the sender:")
        console.print(
            f"\n[yellow1]{signed_slatepack['slatepack'].strip().rstrip()}[yellow1]\n",
        )
        console.print(
            "*** The sender must know [bold]finalize[/bold] the transaction. ***",
            style="italic",
        )

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="post")
def post(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet from which you wish to post the transaction.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    id: int = typer.Option(
        ...,
        help="Id of the transaction you want to be repost",
        prompt="Transaction ID",
    ),
):
    """
    Post a transaction to the network using the Id.
    """

    try:
        token = session.token(wallet=wallet, password=password)
        if post_tx(session_token=token, tx_id=id):
            console.print("Transaction [bold]posted[/bold] successfully ✔")
        else:
            error_console.print("Unable to post the transaction ✗")

    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="details")
def details(
    wallet: str = typer.Option(
        ..., help="Name of the wallet you want query", prompt="Wallet name"
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    id: int = typer.Option(
        ...,
        help="Id of the transaction you want to read",
        prompt="Transaction Id",
    ),
    slatepack: bool = typer.Option(False, help="Return only the Slatepack"),
    slate: bool = typer.Option(False, help="Export transaction Slate"),
):
    """
    Get the information of a transaction using the Transaction Id.
    """

    details: dict = {}

    try:
        session_token = session.token(wallet=wallet, password=password)
        details = get_tx_details(session_token=session_token, tx_id=id)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    if slatepack:
        console.print(
            f"\n[yellow1]{details['armored_slatepack']}[yellow1]\n",
        )
        raise typer.Exit()

    amount = 0
    fee = 0
    if "fee" in details:
        fee = details["fee"]

    if details["amount_debited"] - details["amount_credited"] > 0:
        amount = details["amount_credited"] - details["amount_debited"]
        if "fee" in details:
            amount = amount - fee
    else:
        amount = details["amount_debited"] - details["amount_credited"]
    amount = abs(amount)
    amount = amount / pow(10, 9)
    fee = fee / pow(10, 9)

    table = Table(box=box.HORIZONTALS, expand=True, show_header=False)
    table.add_column("", justify="right", style="bold")
    table.add_column("", justify="left")
    table.add_row("tx_id:", f"{details['id']}")
    table.add_row("slate_id:", f"{details.get('slate_id','')}")
    table.add_row("amount:", f"{amount:10,.9f} ツ")
    table.add_row("fee:", f"{fee:10.9f} ツ")
    table.add_row(
        "created on:", f"{datetime.fromtimestamp(details['creation_date_time'])}"
    )
    table.add_row("type:", f"{details['type'].lower()}")
    if "confirmed_height" in details:
        table.add_row("[bold]confirmed height:", f"{details['confirmed_height']}")
    if details["kernels"] and details["kernels"] is not None:
        kernels = ""
        for kernel in details["kernels"]:
            commitment = kernel["commitment"]
            kernels = f"{commitment}"
        table.add_row("kernels:", kernels)
    if "outputs" in details and details["outputs"] is not None:
        outputs = ""
        for output in details["outputs"]:
            commitment = output["commitment"]
            keychain_path = output["keychain_path"]
            status = output["status"]
            outputs = f"[bold]commitment:[/bold] {commitment}\n[bold]keychain path:[/bold] {keychain_path}\n[bold]status:[/bold] {status.lower()}"
        table.add_row("outputs:", outputs)
    console.print(table)

    if slate:
        import json

        file_name = f"{details['slate_id'].replace('-','_')}.json"
        file_path = Path().resolve().joinpath(file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(details["slate"], f, ensure_ascii=True, indent=4)
        console.print(
            f"*[italic]Slate exported to path: [yellow1]{file_path}[yellow1]\n",
        )

    raise typer.Exit()
