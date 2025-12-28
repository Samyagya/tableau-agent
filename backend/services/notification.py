import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_approval_request(
    approval_id,
    action,
    sku,
    warehouse,
    qty,
    cost,
    src=None
):
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set")
        return

    text = (
        f"*🚨 Approval Required*\n"
        f"*Action:* {action}\n"
        f"*SKU:* {sku}\n"
        f"*Warehouse:* {warehouse}\n"
        f"*Qty:* {qty}\n"
        f"*Cost:* ₹{cost}"
    )

    if src:
        text += f"\n*Source:* {src}"

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve ✅"},
                        "style": "primary",
                        "action_id": "approve_action",
                        "value": f"APPROVE::{approval_id}"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject ❌"},
                        "style": "danger",
                        "action_id": "reject_action",
                        "value": f"REJECT::{approval_id}"
                    }
                ]
            }
        ]
    }

    requests.post(SLACK_WEBHOOK_URL, json=payload)
