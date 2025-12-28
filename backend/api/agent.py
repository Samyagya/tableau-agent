from fastapi import APIRouter
from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from fastapi import HTTPException
from services.options import generate_options
from services.decision import reccomendBest

router = APIRouter(prefix="/agent", tags=["agent"])

store = InventoryStore()


@router.get("/scan")
def scan_inventory():
    items = store.get_all_inventory()
    problems = analyze_inventory(items)

    results = []

    for problem in problems:
        options = generate_options(store, problem)
        decision = reccomendBest(options)

        results.append({
            "problem": problem,
            "options": options,
            "recommendation": decision
        })

    return {
        "status": "ok",
        "results": results
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


@router.post("/execute/transfer")
def execute_transfer(payload: dict):
    sku = payload.get("sku")
    src = payload.get("from")
    dest = payload.get("to")
    qty = payload.get("qty")

    if not all([sku, src, dest, qty]):
        raise HTTPException(
            status_code=400,
            detail="Payload must include sku, from, to, qty"
        )

    if qty <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer quantity must be > 0"
        )

    store.transfer(sku, src, dest, qty)

    return {
        "status": "executed",
        "action": "TRANSFER",
        "sku": sku,
        "from": src,
        "to": dest,
        "qty": qty
    }
