from fastapi import APIRouter, HTTPException
from services.inventory import InventoryStore

router = APIRouter(prefix="/inventory", tags=["inventory"])

store = InventoryStore()

#gets the inventory by sku 
@router.get("/{sku}")
def get_inventory_by_sku(sku: str):
    rows = store.get_by_sku(sku)

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No inventory found for SKU: {sku}"
        )

    return {
        "sku": sku,
        "warehouses": rows
    }
