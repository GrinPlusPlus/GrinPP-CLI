#!/usr/bin/env python3

import json
import subprocess
import time
from pathlib import Path

import psutil
import typer
from rich import box
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from requests import exceptions

from modules.api.foreign.rpc import get_list_of_settings
from modules.api.node.rest import (
    get_node_connected_peers,
    get_node_state,
    get_sync_state,
    shutdown_node,
)
from modules.api.owner.v2 import node
from modules.utils import processes

app = typer.Typer()

console = Console(width=125, style="grey93")
error_console = Console(stderr=True, style="bright_red", width=125)


@app.command(name="stop")
def stop_node():
    """
    Close all running Wallets and stop the running Tor Listeners.
    """
    running: bool = False
    node_process_name: str = "GrinNode"
    if psutil.WINDOWS:
        node_process_name = "GrinNode.exe"
    if len(processes.find(node_process_name)) > 0:
        running = True

    if not running:
        error_console.print("Grin node is not running")
        raise typer.Abort()

    elif running:
        with console.status("Stopping node..."):
            attempt = 0
            while attempt < 10:
                time.sleep(1)
                attempt += 1
                try:
                    shutdown_node()
                    break
                except:
                    pass
    if len(processes.find(node_process_name)) == 0:
        console.print("Node and wallet Tor Listeners successfully [bold]stopped[/bold]")
    else:
        error_console.print("Unable to stop Node.")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="start")
def start_node():
    """
    Launch the Grin node in the background.
    """
    data = json.loads("{}")
    error = None
    with console.status("Starting node..."):
        if not Path(f"{Path(__file__).parent.resolve()}/../bin/GrinNode.exe").is_file():
            error = "Can't find the Node"
            raise typer.Exit()

        if psutil.WINDOWS:
            subprocess.Popen(
                f"{Path('../bin/GrinNode.exe').absolute()} --headless",
                shell=True,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        while data is None:
            try:
                data = get_node_state()
            except Exception:
                pass
    if error:
        error_console.print(error)
        raise typer.Abort()

    console.print("Node successfully [bold]launched[/bold] ✔")

    raise typer.Exit()


@app.command(name="clean")
def clean():
    """
    Delete the local chain data and let the node sync again from scratch.
    """
    with console.status("Stopping node..."):
        while True:
            try:
                shutdown_node()
                break
            except Exception:
                pass

    console.print("Node [bold]stopped[/bold] successfully ✔")


@app.command(name="status")
def get_node_status():
    """
    Get the current status of the running node.
    """

    connerr: exceptions.ConnectionError
    error = ""

    message = "Getting Node Status..."
    percentage = 0.0

    console.print("Ctrl+C to quit...\n", style="grey42 italic", justify="right")
    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[bold white]{message}", total=100, completed=int(percentage)
        )
        while True:
            progress.update(
                task, description=f"[bold white]{message}", completed=percentage
            )
            time.sleep(1)
            try:
                node_status = node.get_status()
                message, percentage = node.parse_node_status(node_status)
            except exceptions.ConnectionError as err:
                error = "Unable to communicate with the API"
                break
            except Exception as e:
                error = str(e)
                break
    if error:
        error_console.print(error)
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="tip")
def get_node_tip():
    """
    Print the heights of the node, this is important to see if the running Node is synchronized or not.
    """

    try:
        data = get_node_state()
        table = Table(box=box.HORIZONTALS, expand=True)
        table.add_column("node height", justify="center")
        table.add_column("network height", justify="center")
        table.add_column("chain height", justify="center")
        table.add_column("current hash", justify="center")

        table.add_row(
            str(data["header_height"]),
            str(data["network"]["height"]),
            str(data["chain"]["height"]),
            data["chain"]["hash"],
        )

        console.print(table)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()


@app.command(name="settings")
def get_node_settings():
    """
    Obtain the node's settings like amount of confirmations, minimum of outbound connections, etc.
    """
    data = json.loads("{}")

    try:
        data = get_list_of_settings()
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    table = Table(box=box.HORIZONTALS, expand=True)
    table.add_column("setting", justify="right")
    table.add_column("value", justify="full", style="bold")

    table.add_row("confirmations required:", str(data["result"]["min_confirmations"]))
    table.add_row("maximum of outbounds:", str(data["result"]["max_peers"]))
    table.add_row(
        "maximum of inbounds:",
        str(data["result"]["max_peers"] - data["result"]["min_peers"]),
    )
    table.add_row(
        "peers preferred:",
        f'[{", ".join(sorted(data["result"]["preferred_peers"]))}]'
        if data["result"]["preferred_peers"] != None
        else "[ ]",
    )
    table.add_row(
        "peers allowed:",
        ", ".join(sorted(data["result"]["allowed_peers"]))
        if data["result"]["allowed_peers"] != None
        else "[ ]",
    )
    table.add_row(
        "peers blocked:",
        ", ".join(sorted(data["result"]["blocked_peers"]))
        if data["result"]["blocked_peers"] != None
        else "[ ]",
    )

    console.print(table)

    raise typer.Exit()


@app.command(name="peers")
def list_connected_peers():
    """
    List the inbound and outbound peers connected to the running node.
    """

    try:
        data = node.get_connected_peers()

        table = Table(box=box.HORIZONTALS, expand=True)
        table.add_column("", justify="center", width=5)
        table.add_column("address", justify="center", width=20)
        table.add_column("agent", justify="center", width=20)
        table.add_column("direction", justify="center", width=20)

        i = 1
        for peer in data:
            table.add_row(str(i), peer["addr"], peer["user_agent"], peer["direction"])
            i += 1

        console.print(table)
    except Exception as err:
        error_console.print(f"Error: {err} ¯\_(ツ)_/¯")
        raise typer.Abort()

    raise typer.Exit()
