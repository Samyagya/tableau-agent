import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

def send_approval_request(action_type, sku, warehouse, quantity, cost, src=None):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Error: SLACK_WEBHOOK_URL not set in .env")
        return False

    # 1. Pack the data (SKU, Qty, Action) into a JSON string
    # We include a timestamp 'ts' to check the 48-hour rule later
    action_payload = {
        "action": action_type,
        "sku": sku,
        "warehouse": warehouse,
        "qty": quantity,
        "cost": cost,
        "from": src,
        "ts": time.time()
    }
    
    # Convert to string so it fits inside the button's hidden value
    payload_string = json.dumps(action_payload)

    # 2. Build the Message (Slack Block Kit)
    message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚨 *APPROVAL NEEDED*\n\n**Proposal:** {action_type} {quantity} units of {sku}\n**Target:** {warehouse}\n**Est. Cost:** ₹{cost}" + (f"\n**Source:** {src}" if src else "")
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Confirm", "emoji": True},
                        "style": "primary",
                        "value": payload_string, # <--- HIDDEN DATA
                        "action_id": "approve_action"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Decline", "emoji": True},
                        "style": "danger",
                        "value": "decline",
                        "action_id": "decline_action"
                    }
                ]
            }
        ]
    }

    try:
        requests.post(webhook_url, json=message)
        return True
    except Exception as e:
        print(f"Notification Failed: {e}")
        return False