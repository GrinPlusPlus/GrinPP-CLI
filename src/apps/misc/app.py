#!/usr/bin/env python3

from typing import Optional

import psutil
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from modules.utils import grinchck, processes
from modules.utils.coingecko import get_grin_price

app = typer.Typer()

console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red")


@app.command(name="wenmoon")
def simple_grin_price(
    currency: str = typer.Option(
        "usd", help="Currency like usd, eur, btc, etc.", prompt=True
    )
):
    """
    Get Grin price from CoinGecko.
    """
    try:
        moon = get_grin_price(currency)
    except Exception as err:
        error_console.print(f"Error: {err}")
        raise typer.Abort()
    table = Table(box=box.HORIZONTALS, show_header=False)
    direction: str = ""
    style: str = ""
    if moon["24h_change"] >= 0:
        style = "green3"
        direction = "⬆︎"
    else:
        style = "bright_red"
        direction = "⬇︎"
    change: str = f"[{style}]{moon['24h_change']:10,.2f}% {direction}"

    table.add_column("", justify="right", style="bold")
    table.add_column("", justify="right")
    table.add_row("Price:", f"{moon['price']:10,.6f}")
    table.add_row("24h Change:", f"{change}")
    table.add_row("Market cap:", f"{moon['market_cap']:10,.6f}")
    table.add_row("24h Volume:", f"{moon['24h_vol']:10,.6f}")

    console.print(table)


@app.command(name="grinchck")
def grinchck_test(
    address: str = typer.Option(
        ..., help="Address of the wallet you want to check", prompt="Wallet address"
    )
):
    """
    Check if a Slatepack Addresss is reachable via the Tor network.
    """
    reachable: bool = False
    try:
        with console.status("Checking wallet reachability..."):
            reachable = grinchck.connect(
                slatepack_address=address, api_url="http://192.227.214.130/"
            )
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    if reachable:
        console.print(
            f"Address [green3]{address}[/green3] is reachable via the Tor Network <(^_^)>"
        )
    else:
        error_console.print(
            f"Addres [dark_orange]{address}[/dark_orange] is not reachable the Tor Network \_(-_-)_/"
        )
    raise typer.Exit()


@app.command(name="tor")
def tor_control(
    stop: Optional[bool] = typer.Option(
        False,
        help="Stop the tor process",
        rich_help_panel="Actions",
    )
):
    """
    Check the status of Tor.

    If --stop is used, tor will be stopped
    """
    running: bool = False
    tor_process_name: str = "tor"
    if psutil.WINDOWS:
        tor_process_name = "tor.exe"
    tor_processes: list[psutil.Process] = processes.find(tor_process_name)

    if len(tor_processes) > 0:
        running = True

    if not running:
        error_console.print("Tor is not running")
        raise typer.Abort()
    elif running:
        for process in tor_processes:
            console.print(f"Tor is running (PID: [bold]{process.pid})")
        if stop:
            with console.status("Stopping tor..."):
                for process in tor_processes:
                    processes.kill(process.pid)
            if len(processes.find(tor_process_name)) > 0:
                error_console.print("Tor is still running")
            else:
                console.print("Tor [bold]stopped[/bold] successfully ✔")

    raise typer.Exit()
