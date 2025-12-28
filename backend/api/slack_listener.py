from fastapi import APIRouter, Form
from services.inventory import InventoryStore
import json
import time

router = APIRouter()
store = InventoryStore()

@router.post("/slack/interactivity")
async def slack_webhook(payload: str = Form(...)):
    # Payload
    data = json.loads(payload)
    
    user = data.get("user", {}).get("username", "User")
    actions = data.get("actions", [])
    
    if not actions:
        return {"status": "ignored"}

    action_id = actions[0]["action_id"]

    # --- CASE 1: DECLINE ---
    if action_id == "decline_action":
        return {
            "replace_original": "true",
            "text": f"🚫 *DECLINED* by @{user}. No action taken."
        }

    # --- CASE 2: APPROVE ---
    if action_id == "approve_action":
        # Unpack the hidden data
        value_str = actions[0]["value"]
        details = json.loads(value_str)
        
        # A. Check 48-Hour Expiry
        created_time = details.get("ts", 0)
        current_time = time.time()
        hours_passed = (current_time - created_time) / 3600
        
        if hours_passed > 48:
            return {
                "replace_original": "true",
                "text": f"⌛ *EXPIRED*. This request is older than 48 hours and has been auto-declined."
            }

        # B. Execute the Trade
        sku = details["sku"]
        warehouse = details["warehouse"]
        qty = details["qty"]
        action_type = details["action"]
        src = details.get("from")

        try:
            if action_type == "RESTOCK":
                store.restock(sku, warehouse, qty)
            elif action_type == "TRANSFER":
                store.transfer(sku, src, warehouse, qty)
            
            return {
                "replace_original": "true",
                "text": f"✅ *CONFIRMED* by @{user}.\nSuccessfully executed {action_type} for {qty} {sku}."
            }
        except Exception as e:
            return {
                "replace_original": "false",
                "text": f"⚠️ Execution Failed: {str(e)}"
            }

    return {"status": "ok"}