from fastapi import APIRouter, HTTPException, Request
import json
from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from services.options import generate_options
from services.decision import recommend_best
from services.executions import ExecutionLogger
from services.approvals import ApprovalStore
from services.notification import send_approval_request



router = APIRouter(prefix="/agent", tags=["agent"])
approval_store = ApprovalStore()
logger = ExecutionLogger()
store = InventoryStore()


def get_target_warehouse(decision: dict) -> str:
    if decision["type"] == "RESTOCK":
        return decision["warehouse"]
    if decision["type"] == "TRANSFER":
        return decision["to"]
    return "UNKNOWN"


@router.get("/scan")
def scan_inventory():
    items = store.get_all_inventory()
    problems = analyze_inventory(items)

    results = []

    for problem in problems:
        options = generate_options(store, problem)
        decision = recommend_best(options)  # USE CANONICAL NAME

        approval_id = None

        if decision:
            target_warehouse = get_target_warehouse(decision)

            approval_payload = {
                "type": decision["type"],
                "sku": decision["sku"],
                "warehouse": target_warehouse,
                "qty": decision["qty"],
                "cost": decision["cost"],
                "from": decision.get("from"),
                "to": decision.get("to")
            }

            approval_id = approval_store.create(approval_payload)

            send_approval_request(
                approval_id=approval_id,
                action=decision["type"],
                sku=decision["sku"],
                warehouse=target_warehouse,
                qty=decision["qty"],
                cost=decision["cost"],
                src=decision.get("from")
            )

        results.append({
            "problem": problem,
            "options": options,
            "recommendation": decision,
            "approval_id": approval_id
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
    approval_id = payload.get("approval_id")  

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
    if approval_id:
        if not approval_store.is_approved(approval_id):
            raise HTTPException(
                status_code=403,
                detail="Approval not found or not approved"
            )

   
    new_qty = store.restock(sku, warehouse, amount)

    
    logger.log(
        approval_id=approval_id,
        action="RESTOCK",
        sku=sku,
        warehouse=warehouse,
        qty=amount
    )

    return {
        "status": "executed",
        "action": "RESTOCK",
        "sku": sku,
        "warehouse": warehouse,
        "amount_added": amount,
        "new_qty": new_qty,
        "approval_id": approval_id
    }



@router.post("/execute/transfer")
def execute_transfer(payload: dict):
    sku = payload.get("sku")
    src = payload.get("from")
    dest = payload.get("to")
    qty = payload.get("qty")
    approval_id = payload.get("approval_id")  

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

    if approval_id:
        if not approval_store.is_approved(approval_id):
            raise HTTPException(
                status_code=403,
                detail="Approval not found or not approved"
            )

    store.transfer(sku, src, dest, qty)

   
    logger.log(
        approval_id=approval_id,
        action="TRANSFER",
        sku=sku,
        warehouse=dest,
        qty=qty,
        source=src
    )

    return {
        "status": "executed",
        "action": "TRANSFER",
        "sku": sku,
        "from": src,
        "to": dest,
        "qty": qty,
        "approval_id": approval_id
    }

@router.post("/slack/actions")
async def slack_actions(request: Request):
   #Handles Slack
    print("SLACK ACTION RECEIVED")

    form = await request.form()
    payload = json.loads(form["payload"])

    action_value = payload["actions"][0]["value"]
    action_type, approval_id = action_value.split("::")
    user = payload["user"]["username"]

    if action_type == "APPROVE":
        decision = approval_store.approve(approval_id, user)

        if not decision:
            return { "text": "Approval already processed or invalid." }

        return {
            "text": (
                "✅ *Approved*\n"
                f"Action: *{decision['action_type']}*\n"
                f"SKU: *{decision['sku']}*\n"
                f"Qty: *{decision['qty']}*"
            )
        }

    if action_type == "REJECT":
        approval_store.reject(approval_id, user)
        return { "text": "❌ *Rejected*" }

    return { "text": "⚠️ Unknown action" }
