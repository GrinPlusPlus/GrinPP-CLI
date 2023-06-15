"""
Simple actions such as finding and killing processes are useful for troubleshooting. 
"""
from __future__ import annotations

import os
import signal
from collections.abc import Callable

import psutil


def find(name: str) -> list[psutil.Process]:
    """
    Return a list of processes matching with 'name'.

    Parameters
    ----------
    name : str
        Name of the process.

    Returns
    -------
    bool
        A list of `psutil.Process`.
    """
    name = name.casefold()
    result: list[psutil.Process] = []
    processes = {process.pid: process for process in psutil.process_iter()}
    for process in processes.values():
        if not process.is_running():
            continue
        try:
            if process.name().casefold() == name:
                result.append(process)
            elif os.path.basename(process.exe()).casefold() == name:
                result.append(process)
            elif process.cmdline() and process.cmdline()[0].casefold() == name:
                result.append(process)
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:
            continue

    return result


def kill(
    pid: int,
    sig: signal.Signals = signal.SIGTERM,
    include_parent: bool = True,
    timeout: float | None = None,
    on_terminate: Callable[[psutil.Process], object] | None = None,
) -> tuple[list[psutil.Process], list[psutil.Process]]:
    """
    Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.

    Return a (gone, alive) tuple indicating which processes
    are gone and which ones are still alive.

    Parameters
    ----------
    pid : int
        PID of the process.
    sig : signal.Signals
        SIGTERM by default.
    include_parent : bool
        Kill also the parent processs.
    timeout : float | None
        Function will return as soon as all processes terminate or when *timeout* occurs.
    on_terminate : Callable[[psutil.Process], object] | None
        *callback* or function which gets called every time a process terminates.

    Returns
    -------
    bool
        A `(gone, alive)` tuple indicating which processes are gone and which ones are still alive.
    """
    assert pid != os.getpid(), "I won't kill myself!"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
    return (gone, alive)
