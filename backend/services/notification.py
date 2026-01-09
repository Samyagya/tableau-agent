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


def send_recommendations_dropdown(recommendations: list[dict]):
    
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set")
        return

    options = []

    for r in recommendations:
        if r["type"] == "TRANSFER":
            label = f"TRANSFER {r['sku']} | {r['from']} → {r['to']} ({r['qty']})"
            value = f"TRANSFER|{r['sku']}|{r['from']}|{r['to']}|{r['qty']}"

        elif r["type"] == "RESTOCK":
            label = f"RESTOCK {r['sku']} | {r['warehouse']} ({r['qty']})"
            value = f"RESTOCK|{r['sku']}|{r['warehouse']}|{r['qty']}"

        else:
            continue

        options.append({
            "text": {"type": "plain_text", "text": label},
            "value": value
        })

    if not options:
        return

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🧠 Agent Recommendations*\nSelect one action and approve or reject."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "static_select",
                        "action_id": "select_recommendation",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Choose a recommendation"
                        },
                        "options": options
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve ✅"},
                        "style": "primary",
                        "action_id": "approve_action",
                        "value": "APPROVE"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject ❌"},
                        "style": "danger",
                        "action_id": "reject_action",
                        "value": "REJECT"
                    }
                ]
            }
        ]
    }

    requests.post(SLACK_WEBHOOK_URL, json=payload)

def update_slack_message(response_url: str, text: str):
    payload = {
        "replace_original": True,
        "text": text,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
    }

    requests.post(response_url, json=payload)