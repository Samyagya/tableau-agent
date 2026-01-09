def build_dropdown_options(recommendations: list[dict]):
    options = []

    for r in recommendations:
        if r["type"] == "TRANSFER":
            text = (
                f"TRANSFER {r['sku']} | "
                f"{r['from']} → {r['to']} ({r['qty']})"
            )
            value = (
                f"TRANSFER|{r['sku']}|{r['from']}|{r['to']}|{r['qty']}"
            )

        elif r["type"] == "RESTOCK":
            text = (
                f"RESTOCK {r['sku']} | "
                f"{r['warehouse']} ({r['qty']})"
            )
            value = (
                f"RESTOCK|{r['sku']}|{r['warehouse']}|{r['qty']}"
            )

        else:
            continue

        options.append({
            "text": { "type": "plain_text", "text": text },
            "value": value
        })

    return options
