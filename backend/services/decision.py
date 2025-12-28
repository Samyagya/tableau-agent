def reccomendBest(options: list[dict]) -> dict | None:
    if not options:
        return None

    sorted_options = sorted(
        options,
        key=lambda o: (
            o["cost"],
            0 if o["type"] == "TRANSFER" else 1
        )
    )

    chosen = sorted_options[0]

    return {
        **chosen,
        "decision_reason": (
            "Chosen due to lowest cost"
            + (
                " and internal transfer preferred"
                if chosen["type"] == "TRANSFER"
                else ""
            )
        )
    }
