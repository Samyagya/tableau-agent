def analyze_inventory(items: list[dict]):
    

    recommendations = []

    for item in items:
        try:
            sku = item["SKU"]
            warehouse = item["Warehouse"]
            qty = int(item["Qty"])
            safety = int(item.get("Safety_Stock") or 0)
            shipping = int(item.get("Shipping_Cost") or 0)
            avg_sales = int(item.get("Avg_Sales") or 5)
        except Exception:
            continue  

        #SKip check if the stock is above the safety threshold
        if qty >= safety:
            continue

        # Strategy logic (Taken from samyagya's code)
        if shipping > 15:
            days_to_cover = 30
            strategy = "Bulk Restock"
        else:
            days_to_cover = 10
            strategy = "Lean Restock"

        target_stock = avg_sales * days_to_cover
        amount = target_stock - qty

        if amount <= 0:
            continue

        recommendations.append({
            "sku": sku,
            "warehouse": warehouse,
            "action": "RESTOCK",
            "amount": amount,
            "strategy": strategy,
            "reason": f"Stock below safety threshold ({qty} < {safety})"
        })

    return recommendations
