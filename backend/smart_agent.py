from services.inventory import InventoryStore
from services.analysis import analyze_inventory
from datetime import datetime

def smart_job():
    store = InventoryStore()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 GLOBAL AGENT: Scanning supply chain...")

    items = store.get_all_inventory()
    recommendations = analyze_inventory(items, store)

    print("\n📋 AGENT RECOMMENDATIONS:")
    if not recommendations:
        print("   ✅ No actions required. Inventory is healthy.")
    else:
        for rec in recommendations:
            print(
                f"   ▶ SKU: {rec['sku']} | Warehouse: {rec['warehouse']} | "
                f"Action: {rec['action']} | Qty: {rec['amount']} | "
                f"Strategy: {rec.get('strategy', 'N/A')} | "
                f"Cost: ₹{rec['cost']} | Reason: {rec['reason']}"
        )


    for rec in recommendations:
        if rec["action"] == "TRANSFER":
            print(f"🔁 TRANSFER: {rec['amount']} {rec['sku']} from {rec['from']} → {rec['warehouse']}")
            store.transfer(rec["sku"], rec["from"], rec["warehouse"], rec["amount"])

        elif rec["action"] == "RESTOCK":
            print(f"📦 RESTOCK ({rec['strategy']}): {rec['amount']} {rec['sku']} → {rec['warehouse']}")
            store.restock(rec["sku"], rec["warehouse"], rec["amount"])


# if __name__ == "__main__":
#     print("🤖 SYSTEM ONLINE: Universal Supply Chain Agent is running...")
#     try:
#         while True:
#             smart_job()
#             # Wait 10 seconds before scanning the whole world again
#             time.sleep(10)
#     except KeyboardInterrupt:
#         print("\n🛑 SYSTEM SHUTDOWN: Agent stopped by user.")

