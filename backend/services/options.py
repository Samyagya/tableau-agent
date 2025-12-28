from services.routing import find_nearest_supplier
from services.costing import internal_transfer_cost, external_restock_cost


def generate_options(store, problem: dict) -> list[dict]:
    sku = problem["sku"]
    warehouse = problem["warehouse"]
    required_qty = problem["required_qty"]
    shipping_cost = problem["shipping_cost"]
    avg_sales = problem["avg_sales"]

    options = []


# otp 1: internal transfer
    supplier = find_nearest_supplier(
        store,
        sku,
        warehouse,
        required_qty
    )

    if supplier:
        transfer_cost = internal_transfer_cost(
            store,
            sku,
            supplier,
            warehouse,
            required_qty
        )

        options.append({
            "type": "TRANSFER",
            "sku": sku,
            "from": supplier,
            "to": warehouse,
            "qty": required_qty,
            "cost": transfer_cost,
            "strategy": "LEAN"
        })

    # otp 2: external restock
    if shipping_cost > 15:
        strategy = "BULK"
        days_to_cover = 30
    else:
        strategy = "LEAN"
        days_to_cover = 10

    target_stock = avg_sales * days_to_cover
    restock_qty = max(target_stock, required_qty)

    restock_cost = external_restock_cost(
        store,
        sku,
        warehouse,
        restock_qty
    )

    options.append({
        "type": "RESTOCK",
        "sku": sku,
        "warehouse": warehouse,
        "qty": restock_qty,
        "cost": restock_cost,
        "strategy": strategy
    })

    return options
