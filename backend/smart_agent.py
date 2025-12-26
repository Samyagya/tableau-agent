from services.inventory import InventoryStore
import time
from datetime import datetime

def smart_job():
    store = InventoryStore()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 GLOBAL AGENT: Scanning entire supply chain...")

    # 1. Get EVERY row from the database
    all_items = store.get_all_inventory()
    
    # 2. Loop through each item (Universal Logic)
    for item in all_items:
        sku = item['SKU']
        warehouse = item['Warehouse']
        
        # safely convert to int (handles empty cells or text)
        try:
            current_qty = int(item['Qty'])
            # Default to 0 if Safety_Stock is missing
            safety_threshold = int(item['Safety_Stock'] or 0) 
            # Default to 0 shipping if missing
            shipping_cost = int(item['Shipping_Cost'] or 0)   
            # Default to 5 sales/day if missing
            avg_sales = int(item.get('Avg_Sales') or 5)       
        except ValueError:
            print(f"   ⚠️ DATA ERROR: Skipping invalid row for {sku} in {warehouse}")
            continue

        # Skip rows that don't need attention (Optimization)
        if current_qty >= safety_threshold:
            # Optional: Print healthy status only sometimes to reduce noise
            # print(f"   ✅ OK: {sku} in {warehouse} is healthy.")
            continue
            
        # --- THE SMART LOGIC (Applied to everyone) ---
        print(f"   🔎 PROBLEM FOUND: {sku} in {warehouse} (Qty: {current_qty} < Safe: {safety_threshold})")
        print(f"      Data: Sales={avg_sales}/day | Shipping=${shipping_cost}")

        # Strategy Selection
        if shipping_cost > 15:
            days_to_cover = 30
            strategy = "Bulk Buy (Save Shipping)"
        else:
            days_to_cover = 10
            strategy = "Lean Restock (Just-in-Time)"

        # Calculation
        target_stock = avg_sales * days_to_cover
        amount_to_buy = target_stock - current_qty

        # Safety Check: Don't order 0 or negative
        if amount_to_buy > 0:
            print(f"      ⚙️ STRATEGY: {strategy}")
            print(f"      💳 ACTION: Ordering {amount_to_buy} units...")
            
            # EXECUTE for this specific warehouse/SKU
            store.restock(sku, warehouse, amount_to_buy)
        else:
            print("      ⚠️ ERROR: Calculated restock amount is 0. Check logic.")

if __name__ == "__main__":
    print("🤖 SYSTEM ONLINE: Universal Supply Chain Agent is running...")
    try:
        while True:
            smart_job()
            # Wait 10 seconds before scanning the whole world again
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 SYSTEM SHUTDOWN: Agent stopped by user.")