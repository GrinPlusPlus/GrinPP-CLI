"""
This modules defines some useful tools to use with the CoinGecko API.
"""

import requests

SUPPORTED_CURRENCIES = [
    "btc",
    "eth",
    "ltc",
    "bch",
    "bnb",
    "eos",
    "xrp",
    "xlm",
    "link",
    "dot",
    "yfi",
    "usd",
    "aed",
    "ars",
    "aud",
    "bdt",
    "bhd",
    "bmd",
    "brl",
    "cad",
    "chf",
    "clp",
    "cny",
    "czk",
    "dkk",
    "eur",
    "gbp",
    "hkd",
    "huf",
    "idr",
    "ils",
    "inr",
    "jpy",
    "krw",
    "kwd",
    "lkr",
    "mmk",
    "mxn",
    "myr",
    "ngn",
    "nok",
    "nzd",
    "php",
    "pkr",
    "pln",
    "rub",
    "sar",
    "sek",
    "sgd",
    "thb",
    "try",
    "twd",
    "uah",
    "vef",
    "vnd",
    "zar",
    "xdr",
    "xag",
    "xau",
    "bits",
    "sats",
]
"""List of the supported currencies by CoinGecko API."""


def __is_currency_supported(currency: str) -> bool:
    """
    Return whether or nothe the currency is supported by CoinGecko API

    Parameters
    ----------
    currency : str
        The VS currency, for example eur, usd, btc or eth.

    Returns
    -------
    bool
        a boolean value containing True if the currency is supported or False if it not supported.
    """

    return currency in SUPPORTED_CURRENCIES


def get_grin_price(currency: str) -> dict:
    """
    Get the price of Grin using the CoinGecko API

    Parameters
    ----------
    currency : str
        The VS currency, for example eur, usd, btc or eth.

    Raises
    ------
    Exception
        If the currency uses is not supported.

    Returns
    ------
    dict
        A dictionary with: price, market cap, 24h change and 24h volume.
    """

    if not __is_currency_supported(currency=currency):
        raise Exception(f"{currency} is not a supported currency by CoinGecko API")

    result: dict = requests.get(
        url=f"https://api.coingecko.com/api/v3/simple/price?ids=grin&vs_currencies={currency}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true&precision=true"
    ).json()

    return {
        "price": result["grin"][currency],
        "market_cap": result["grin"][currency + "_market_cap"],
        "24h_change": result["grin"][currency + "_24h_change"],
        "24h_vol": result["grin"][currency + "_24h_vol"],
    }
