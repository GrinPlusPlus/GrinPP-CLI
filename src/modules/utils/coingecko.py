#!/usr/bin/env python3


import requests


def is_currency_supported(currency: str) -> bool:
    return currency in [
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


def get_grin_price(currency: str) -> dict:
    results: dict = requests.get(
        url=f"https://api.coingecko.com/api/v3/simple/price?ids=grin&vs_currencies={currency}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true&precision=true"
    ).json()
    results["price"] = results["grin"][currency]
    results["market_cap"] = results["grin"][currency + "_market_cap"]
    results["24h_change"] = results["grin"][currency + "_24h_change"]
    results["24h_vol"] = results["grin"][currency + "_24h_vol"]
    return results
