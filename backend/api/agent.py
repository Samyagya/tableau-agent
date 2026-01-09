from fastapi import APIRouter, HTTPException, Request,BackgroundTasks
import json
from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from services.options import generate_options
from services.decision import recommend_best
from services.executions import ExecutionLogger
from services.approvals import ApprovalStore
from services.notification import send_approval_request
from services.notification import send_recommendations_dropdown
from services.notification import update_slack_message
from services.inventory import InventoryStore
from services.approvals import ApprovalStore

def parse_selected(parts: list[str]) -> dict:
    
    if parts[0] == "TRANSFER":
        return {
            "type": "TRANSFER",
            "sku": parts[1],
            "from": parts[2],
            "to": parts[3],
            "qty": int(parts[4])
        }

    if parts[0] == "RESTOCK":
        return {
            "type": "RESTOCK",
            "sku": parts[1],
            "warehouse": parts[2],
            "qty": int(parts[3])
        }

    raise ValueError(f"Unknown selection format: {parts}")



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
    recommendations = []

    for problem in problems:
        options = generate_options(store, problem)
        decision = recommend_best(options)  
        results.append({
            "problem": problem,
            "options": options,
            "recommendation": decision
        })

        if decision:
            recommendations.append(decision)

    if recommendations:
        send_recommendations_dropdown(recommendations)

    return {
        "status": "ok",
        "results": results,
        "recommendation_count": len(recommendations)
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
async def slack_actions(
    request: Request,
    background_tasks: BackgroundTasks
):
   
    form = await request.form()
    payload = json.loads(form["payload"])

    background_tasks.add_task(handle_slack_action, payload)
    return {}  


def handle_slack_action(payload: dict):
    action = payload["actions"][0]
    action_id = action["action_id"]
    message_ts = payload["message"]["ts"]
    response_url = payload["response_url"]

    
    if action_id == "select_recommendation":
        selected_value = action["selected_option"]["value"]

        store.save_slack_selection(message_ts, selected_value)

        update_slack_message(
            response_url,
            "✅ *Selection saved*\nClick **Approve** or **Reject**."
        )
        return

    if action_id == "approve_action":
        selected_value = store.get_slack_selection(message_ts)

        if not selected_value:
            update_slack_message(
                response_url,
                "⚠️ *No selection found.* Please select an option first."
            )
            return

        decision = parse_selected(selected_value.split("|"))
        approval_id = approval_store.create(decision)

        text = (
            "✅ *APPROVED*\n\n"
            f"*Action:* {decision['type']}\n"
            f"*SKU:* {decision['sku']}\n"
            f"*Quantity:* {decision['qty']}\n"
        )

        if decision["type"] == "TRANSFER":
            text += (
                f"*From:* {decision['from']}\n"
                f"*To:* {decision['to']}\n"
            )
        else:
            text += f"*Warehouse:* {decision['warehouse']}\n"

        text += f"\n*Approval ID:* `{approval_id}`"

        update_slack_message(response_url, text)
        return

    if action_id == "reject_action":
        selected_value = store.get_slack_selection(message_ts)

        text = "❌ *REJECTED*\n"

        if selected_value:
            decision = parse_selected(selected_value.split("|"))
            text += (
                f"\n*Action:* {decision['type']}"
                f"\n*SKU:* {decision['sku']}"
                f"\n*Quantity:* {decision['qty']}"
            )

            if decision["type"] == "TRANSFER":
                text += (
                    f"\n*From:* {decision['from']}"
                    f"\n*To:* {decision['to']}"
                )
            else:
                text += f"\n*Warehouse:* {decision['warehouse']}"

        update_slack_message(response_url, text)
        return



