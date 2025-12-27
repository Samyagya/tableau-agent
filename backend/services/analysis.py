from services.routing import find_nearest_supplier
from services.costing import internal_transfer_cost, external_restock_cost


def choose_restock_strategy(shipping_cost, avg_sales):
    if shipping_cost > 15:
        return "BULK", 30
    else:
        return "LEAN", 10


def analyze_inventory(items: list[dict], store):
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

        # Skip healthy inventory
        if qty >= safety:
            continue

        # Minimum required to be safe
        required_qty = safety - qty

        # Internal transfer (always lean)
        supplier = find_nearest_supplier(
            store, sku, warehouse, required_qty
        )

        internal_cost = float("inf")
        if supplier:
            internal_cost = internal_transfer_cost(
                store, sku, supplier, warehouse, required_qty
            )

        # External restock (bulk vs lean)
        strategy, days_to_cover = choose_restock_strategy(
            shipping, avg_sales
        )

        target_stock = avg_sales * days_to_cover
        external_qty = max(target_stock - qty, required_qty)

        external_cost = external_restock_cost(
            store, sku, warehouse, external_qty
        )

        # Decision to balance vs buy
        if supplier and internal_cost < external_cost:
            recommendations.append({
                "sku": sku,
                "warehouse": warehouse,
                "action": "TRANSFER",
                "from": supplier,
                "amount": required_qty,
                "cost": internal_cost,
                "strategy": "LEAN",
                "reason": (
                    f"Internal transfer cheaper "
                    f"(₹{internal_cost} < ₹{external_cost})"
                )
            })

        else:
            recommendations.append({
                "sku": sku,
                "warehouse": warehouse,
                "action": "RESTOCK",
                "amount": external_qty,
                "cost": external_cost,
                "strategy": strategy,
                "reason": (
                    f"{strategy} restock chosen "
                    f"(₹{external_cost})"
                )
            })

    return recommendations
