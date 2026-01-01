from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from services.options import generate_options
from services.decision import recommend_best
from services.notification import send_approval_request 
from datetime import datetime
import time

def smart_job():
    store = InventoryStore()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] GLOBAL AGENT: Scanning supply chain...")

    # 1. Get Data
    items = store.get_all_inventory()
    
    # 2. Find Problems
    problems = analyze_inventory(items)

    if not problems:
        print("No actions required. Inventory is healthy.")
        return

    # 3. Process Each Problem
    for problem in problems:
        print(f"PROBLEM: {problem['sku']} in {problem['warehouse']} is critical (Qty: {problem['qty']})")
        
        # Generate Solutions
        options = generate_options(store, problem)
        best_decision = recommend_best(options)

        if best_decision:
            action_type = best_decision['type']
            amount = best_decision['qty']
            sku = best_decision['sku']
            cost = best_decision['cost']
            
            # Smart handling of warehouse names based on action type
            # If RESTOCK, target is 'warehouse'. If TRANSFER, target is 'to' (destination)
            target_warehouse = best_decision.get('warehouse') or best_decision.get('to') 
            source_warehouse = best_decision.get('from') # Only exists for transfers

            print(f"PROPOSAL: {action_type} {amount} units. (Cost: ₹{cost})")
            
            # 4. SEND NOTIFICATION (Fire & Forget)
            print("Sending interactive request to Slack...")
            
            # We send the source warehouse too, so the button knows where to take stock from
            success = send_approval_request(
                action_type, 
                sku, 
                target_warehouse, 
                amount, 
                cost, 
                src=source_warehouse
            )
            
            if success:
                print("Alert Sent. Waiting for manager approval via Slack.")
            else:
                print("Failed to send alert.")

        else:
            print("NO SOLUTION: Could not find a supplier or restock option.")

if __name__ == "__main__":
    print("🤖 SYSTEM ONLINE: Smart Supply Chain Agent (Interactive Mode)...")
    try:
        while True:
            smart_job()
            # Wait 30 seconds to avoid spamming Slack while testing
            print("💤 Sleeping for 30 seconds...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n SYSTEM SHUTDOWN: Agent stopped by user.")