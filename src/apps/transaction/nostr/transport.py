#!/usr/bin/env python3

import json
import ssl
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional

import tornado.ioloop
import typer
from pynostr.base_relay import RelayPolicy
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event, EventKind
from pynostr.filters import Filters, FiltersList
from pynostr.key import PrivateKey
from pynostr.message_pool import EventMessage, MessagePool, NoticeMessage
from pynostr.message_type import ClientMessageType, RelayMessageType
from pynostr.relay import Relay
from pynostr.relay_manager import RelayManager
from pynostr.utils import get_public_key, get_timestamp
from rich import box
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from tornado import gen

from modules import nostr
from modules.api import TransactionsFilterOptions
from modules.api.owner.rpc import (
    add_initial_signature,
    add_signature_to_transaction,
    broadcast_transaction,
    cancel_transaction,
    estimate_transaction_fee,
    get_transaction_details,
    get_wallet_slatepack_address,
    get_wallet_transactions,
    send_coins,
)
from modules.wallet import session

plugin = typer.Typer()

console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red", width=125)


@plugin.command(name="send")
def send_tx_to_nostr(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet from which you wish to get the transaction.",
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
    recipient_npub: str = typer.Option(
        ...,
        help="Recipient Public Key. npub or hex key.",
        prompt="Recipient's npub key",
    ),
    relay_url: str = typer.Option(
        ...,
        help="The Nostr relay to connect to.",
        prompt="Relay to connect to",
    ),
):
    """
    Send an unfinalized transaction through Nosrt
    """

    transaction: dict = {}
    recipient = get_public_key(identity_str=recipient_npub)

    if not recipient:
        error_console.print("Invalid recipient npub key")
        raise typer.Abort()

    console.print(
        f"Recipient Nostr public key: [dark_orange3]{recipient_npub}[/dark_orange3] (∩｀-´)⊃━☆ﾟ.*･｡ﾟ"
    )

    try:
        session_token = session.token(wallet=wallet, password=password)
        transaction = get_transaction_details(session_token=session_token, id=id)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    console.print(f"Transaction with [bold]id={id}[/bold] found ✔")

    address = get_wallet_slatepack_address(session_token)

    wallet_raw_secret = nostr.generate_raw_secret(
        wallet=wallet, address=address, password=password
    )
    nostr_private_key = nostr.retrieve_private_key(
        wallet=wallet, raw_secret=wallet_raw_secret
    )

    console.print(f"Sender [bold]Nostr key[/bold] loaded ✔")

    @gen.coroutine
    def transaction_sent(message_json):
        if message_json[0] == RelayMessageType.OK:
            if len(message_json) == 4 and "blocked" in message_json[3]:
                error_console.print(f" Error: {message_json[3]} ")
                ascii = r"""
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░▄▄▄▄▄▄▄░░░░░░░░░
░░░░░░░░░▄▀▀▀░░░░░░░▀▄░░░░░░░
░░░░░░░▄▀░░░░░░░░░░░░▀▄░░░░░░
░░░░░░▄▀░░░░░░░░░░▄▀▀▄▀▄░░░░░
░░░░▄▀░░░░░░░░░░▄▀░░██▄▀▄░░░░
░░░▄▀░░▄▀▀▀▄░░░░█░░░▀▀░█▀▄░░░
░░░█░░█▄▄░░░█░░░▀▄░░░░░▐░█░░░
░░▐▌░░█▀▀░░▄▀░░░░░▀▄▄▄▄▀░░█░░
░░▐▌░░█░░░▄▀░░░░░░░░░░░░░░█░░
░░▐▌░░░▀▀▀░░░░░░░░░░░░░░░░▐▌░
░░▐▌░░░░░░░░░░░░░░░▄░░░░░░▐▌░
░░▐▌░░░░░░░░░▄░░░░░█░░░░░░▐▌░
░░░█░░░░░░░░░▀█▄░░▄█░░░░░░▐▌░
░░░▐▌░░░░░░░░░░▀▀▀▀░░░░░░░▐▌░
░░░░█░░░░░░░░░░░░░░░░░░░░░█░░
░░░░▐▌▀▄░░░░░░░░░░░░░░░░░▐▌░░
░░░░░█░░▀░░░░░░░░░░░░░░░░▀░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                """
                console.print(ascii)
            else:
                console.print(f"Transaction [bold]sent[/bold] via Nostr ✔")
                ascii = r"""
░░▄░░░▄░▄▄▄▄░░░░░░░░░░░░░░░
░░█▀▄▀█░█▄▄░░░░░░░░░░░░░░░░
░░█░░░█░█▄▄▄░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░
░▄▄▄░▄░░░▄░░▄▄▄░▄▄▄▄▄░░▄▄▄░
█░░░░█░░░█░█░░░░░░█░░░█░░░█
█░▀█░█░░░█░░▀▀▄░░░█░░░█▀▀▀█
░▀▀▀░░▀▀▀░░▄▄▄▀░░░▀░░░▀░░░▀
                """
                console.print(ascii)
            relay.close()
        elif message_json[0] == RelayMessageType.NOTICE:
            error_console.print(f"\nError: {message_json[1]} ¯\_(ツ)_/¯\n")

        relay.close()

    io_loop = tornado.ioloop.IOLoop.current()
    relay = Relay(
        url=relay_url,
        message_pool=MessagePool(),
        io_loop=io_loop,
        policy=RelayPolicy(should_read=True, should_write=True),
        close_on_eose=False,
        message_callback=transaction_sent,
    )

    dm = EncryptedDirectMessage(
        pubkey=nostr_private_key.public_key.hex(),
        recipient_pubkey=recipient.hex(),
        cleartext_content=transaction["armored_slatepack"],
    )
    dm.encrypt(
        private_key_hex=nostr_private_key.hex(),
    )

    event = dm.to_event()

    expiration_date = datetime.now() + timedelta(days=2)
    event.add_tag("expiration", f"{int(expiration_date.timestamp())}")

    event.sign(nostr_private_key.hex())

    with console.status("Sending transaction via Nostr..."):
        relay.publish(event.to_message())
        try:
            io_loop.run_sync(func=relay.connect)
        except gen.Return:
            pass

    raise typer.Exit()


@plugin.command(name="receive")
def grab_txs_from_nostr(
    wallet: str = typer.Option(
        ...,
        help="Name of the wallet in which you want to insert transactions.",
        prompt="Wallet name",
    ),
    password: str = typer.Option(
        ..., help="Wallet password.", prompt="Password", hide_input=True
    ),
    relay_url: str = typer.Option(
        ...,
        help="The Nostr relay to connect to.",
        prompt="Relay to connect to",
    ),
):
    """
    Grab pending transactions from Nostr
    """

    messages: list = []
    nostr_private_key: PrivateKey = None

    try:
        session_token = session.token(wallet=wallet, password=password)
        address = get_wallet_slatepack_address(session_token)
        wallet_raw_secret = nostr.generate_raw_secret(
            wallet=wallet, address=address, password=password
        )
        nostr_private_key = nostr.retrieve_private_key(
            wallet=wallet, raw_secret=wallet_raw_secret
        )

        if not nostr_private_key:
            raise Exception("Nostr private not loaded")
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    console.print(f"Receiver [bold]Nostr key[/bold] loaded ✔")

    def decrypt_dm(message_json):
        if message_json[0] == RelayMessageType.EVENT:
            event = Event.from_dict(message_json[2])
            if event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                message = EncryptedDirectMessage.from_event(event)
                message.decrypt(
                    private_key_hex=nostr_private_key.hex(), public_key_hex=event.pubkey
                )
                messages.append(
                    {
                        "slatepack": message.cleartext_content,
                        "sender": event.pubkey,
                        "id": event.id,
                    }
                )

    filters = FiltersList(
        [
            Filters(
                kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                until=get_timestamp(),
                pubkey_refs=[
                    nostr_private_key.public_key.hex(),
                ],
            )
        ]
    )

    relay_manager = RelayManager(error_threshold=3, timeout=0)
    relay_manager.add_relay(
        url=relay_url,
        close_on_eose=True,
        message_callback=decrypt_dm,
    )

    subscription_id = uuid.uuid4().hex
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)
    with console.status("Grabbing slatepacks..."):
        relay_manager.run_sync()
    relay_manager.close_subscription_on_all_relays(subscription_id)
    relay_manager.close_all_relay_connections()
    relay_manager.remove_closed_relays()

    console.print(f"Slatepacks found: [bold]{len(messages)}[/bold]")
    if not messages:
        raise typer.Exit()

    new_txs = []

    for message in messages:
        try:
            message["signed_slate"] = add_initial_signature(
                session_token=session_token, slatepack=message["slatepack"]
            )
            new_txs.append(message)
        except:
            pass

    console.print(f"New Transactions received: [bold]{len(new_txs)}[/bold]")
    if not new_txs:
        raise typer.Exit()

    if Confirm.ask(
        f"Would you like to review them and send back the signed Slatepack via Nostr?",
        default=True,
    ):

        def check_reply(message_json):
            if message_json[0] == RelayMessageType.OK:
                console.print(f"Slate sent via Nostr ✔")
            elif message_json[0] == RelayMessageType.NOTICE:
                error_console.print(f"\nError: {message_json[1]} ¯\_(ツ)_/¯\n")

        relay_manager.add_relay(
            url=relay_url,
            close_on_eose=True,
            message_callback=check_reply,
            policy=RelayPolicy(should_read=False, should_write=False),
        )

        subscription_id = uuid.uuid4().hex
        relay_manager.add_subscription_on_all_relays(subscription_id, filters)

        for idx, item in enumerate(new_txs):
            console.print("")
            sender: str = "-"
            if "sender" in item["signed_slate"]:
                sender = item["signed_slate"]["sender"]["slatepack"]
            amount: float = float(item["signed_slate"]["slate"]["amt"]) / pow(10, 9)
            fee: float = float(item["signed_slate"]["slate"]["fee"]) / pow(10, 9)
            table = Table(
                box=box.HORIZONTALS,
                expand=True,
                show_header=False,
                title=f"Slate Id: [bold]{item['signed_slate']['slate']['id']}[/bold]",
            )
            table.add_column("", justify="right", style="bold")
            table.add_column("", justify="left")
            table.add_row("amount:", f"{amount:10,.9f} ツ")
            table.add_row("fee:", f"{fee:10.9f} ツ")
            table.add_row("sender:", f"{sender}")
            console.print(f"[bold]Transaction #{idx+1}[/bold]")
            console.print(table)

            if Confirm.ask(
                f"Would you like to send back the signed Slatepack via Nostr?",
                default=True,
            ):
                dm = EncryptedDirectMessage(
                    pubkey=nostr_private_key.public_key.hex(),
                    recipient_pubkey=item["sender"],
                    cleartext_content=item["signed_slate"]["slatepack"],
                )
                dm.encrypt(
                    private_key_hex=nostr_private_key.hex(),
                )

                reply = dm.to_event()

                expiration_date = datetime.now() + timedelta(days=2)
                reply.add_tag("expiration", f"{int(expiration_date.timestamp())}")
                # create 'e' tag reference to the note you're replying to
                reply.add_event_ref(item["id"])
                # create 'p' tag reference to the pubkey you're replying to
                reply.add_pubkey_ref(item["sender"])
                reply.sign(nostr_private_key.hex())

                relay_manager.publish_event(reply)
                with console.status("Sending response..."):
                    relay_manager.run_sync()

        relay_manager.close_subscription_on_all_relays(subscription_id)
        relay_manager.close_all_relay_connections()
        relay_manager.remove_closed_relays()

        console.print("")
