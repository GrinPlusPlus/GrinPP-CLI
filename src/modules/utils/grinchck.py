"""
Mimblewimble transactions are interactive, meaning both parties need some kind of communication to interact with each other and exchange the necessary data to create a transaction. Slatepack addresses are also used to derive a Tor address. By default, the sender's wallet will try to communicate with the receiver's wallet via Tor. However, if the Tor connection between the wallets is not successful for whatever reason, grin defaults to manually exchanging slate text messages, also called slatepacks. manually.

This module uses the Grin Address Checker API to check whether or not an address is accessible through Tor.
"""
from requests import Response, post
from requests.exceptions import ConnectionError


def connect(slatepack_address: str, api_url: str) -> bool:
    """
    Attempts to connect to a wallet through Tor. This will return True if the wallet is reached.

    Parameters
    ----------
    slatepack_address : str
        Slatepack address if the wallet.
    api_url : str
        URL of grinchck API.

    Raises
    ------
    ConnectionError
        If the API is not available.

    Returns
    ------
    bool
        True when the wallet is reachable, otherwise False.
    """
    try:
        data: dict = {"wallet": slatepack_address}
        result: Response = post(url=api_url, data=data)
        return result.status_code == 200
    except ConnectionError:
        error = "Unable to connect to the GrinChck API"
        raise Exception(error)
