def analyze_inventory(items: list[dict]) -> list[dict]:
    problems = []

    for item in items:
        try:
            sku = item["SKU"]
            warehouse = item["Warehouse"]
            qty = int(item["Qty"])
            safety = int(item.get("Safety_Stock") or 0)
            shipping_cost = int(item.get("Shipping_Cost") or 0)
            avg_sales = int(item.get("Avg_Sales") or 0)
        except Exception:
            
            continue

        if qty >= safety:
            continue

        required_qty = safety - qty

        problems.append({
            "sku": sku,
            "warehouse": warehouse,
            "qty": qty,
            "safety_stock": safety,
            "required_qty": required_qty,
            "shipping_cost": shipping_cost,
            "avg_sales": avg_sales
        })

    return problems
