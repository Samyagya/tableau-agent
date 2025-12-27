"""
costing.py
----------
Pure cost evaluation utilities.

These functions DO NOT:
- modify inventory
- call Google Sheets APIs directly
- make decisions

They only compute costs based on current inventory data.
"""


def internal_transfer_cost(store, sku, source_warehouse, dest_warehouse, qty):
    """
    Cost of transferring stock internally from source → destination.
    Assume:
    - Cost is proportional to the source warehouse's shipping cost
    """

    rows = store.get_all_inventory()

    for r in rows:
        if r["SKU"] == sku and r["Warehouse"] == source_warehouse:
            shipping_cost = int(r.get("Shipping_Cost") or 0)
            return shipping_cost * qty

    return float("inf")


def external_restock_cost(store, sku, destination_warehouse, qty):
    """
    Cost of restocking stock externally into a warehouse.
    Assume:
    - Cost is proportional to the destination warehouse's shipping cost
    """

    rows = store.get_all_inventory()

    for r in rows:
        if r["SKU"] == sku and r["Warehouse"] == destination_warehouse:
            shipping_cost = int(r.get("Shipping_Cost") or 0)
            return shipping_cost * qty

    # If destination not found, treat as impossible
    return float("inf")
