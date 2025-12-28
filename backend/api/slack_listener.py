from fastapi import APIRouter, Form
import json
from services.approvals import ApprovalStore

router = APIRouter()
approval_store = ApprovalStore()


@router.post("/slack/interactivity")
async def slack_interactivity(payload: str = Form(...)):
    data = json.loads(payload)

    user = data.get("user", {}).get("username", "user")
    action = data["actions"][0]

    approval_id = action["value"]
    action_id = action["action_id"]

    #reject action
    if action_id == "reject_action":
        rejected = approval_store.reject(approval_id, user)

        if not rejected:
            return {
                "replace_original": True,
                "text": "⚠️ This approval was already processed."
            }

        return {
            "replace_original": True,
            "text": f"❌ *REJECTED* by @{user}. No action taken."
        }

    #approve
    if action_id == "approve_action":
        approved = approval_store.approve(approval_id, user)

        if not approved:
            return {
                "replace_original": True,
                "text": "⚠️ Approval not found or already processed."
            }

        return {
            "replace_original": True,
            "text": f"✅ *APPROVED* by @{user}. Ready for execution."
        }

    return {"status": "ignored"}
