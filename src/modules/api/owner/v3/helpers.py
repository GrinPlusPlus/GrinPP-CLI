def filter_transactions(transactions: list[dict], status: str) -> list:
    transactions.sort(key=lambda t: t["creation_date_time"], reverse=True)

    if status == "coinbase":
        return list(
            filter(lambda t: "coinbase" in str(t["type"]).lower(), transactions)
        )
    elif status == "sent":
        return list(filter(lambda t: "sent" in str(t["type"]).lower(), transactions))
    elif status == "pending":
        return list(
            filter(
                lambda t: "sending" in str(t["type"]).lower()
                or "receiving" in str(t["type"]).lower(),
                transactions,
            )
        )
    elif status == "received":
        return list(
            filter(lambda t: str(t["type"]).lower() == "received", transactions)
        )
    elif status == "canceled":
        return list(
            filter(lambda t: "canceled" in str(t["type"]).lower(), transactions)
        )

    return transactions
