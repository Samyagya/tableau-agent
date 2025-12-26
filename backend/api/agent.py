from fastapi import APIRouter
from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from fastapi import HTTPException

router = APIRouter(prefix="/agent", tags=["agent"])

store = InventoryStore()


@router.get("/scan")
def scan_inventory():
    #gets the whole inventory (Taken from samyagya's code)
    items = store.get_all_inventory()
    recommendations = analyze_inventory(items)

    return {
        "status": "ok",
        "recommendations": recommendations
    }


#controlled restock endpoint (Taken from samyagya's code)
@router.post("/execute/restock")
def execute_restock(payload: dict):

    sku = payload.get("sku")
    warehouse = payload.get("warehouse")
    amount = payload.get("amount")

    if not all([sku, warehouse, amount]):
        raise HTTPException(
            status_code=400,
            detail="Payload must include sku, warehouse, amount"
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Restock amount must be > 0"
        )

    # Item loop (Taken from samyagya's code)
    rows = store.get_by_sku(sku)
    target = [r for r in rows if r["Warehouse"] == warehouse]

    if not target:
        raise HTTPException(
            status_code=404,
            detail="SKU/Warehouse combination not found"
        )

    #code to execute restock (Taken from samyagya's code)
    new_qty = store.restock(sku, warehouse, amount)

    return {
        "status": "executed",
        "action": "RESTOCK",
        "sku": sku,
        "warehouse": warehouse,
        "amount_added": amount,
        "new_qty": new_qty
    }