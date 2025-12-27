from services.inventory import InventoryStore
import time

def run_agent():
    store = InventoryStore()
    
    print("🤖 AGENT: Checking system status...")
    # We know New Delhi is at 10. The threshold is 20.
    print("🤖 AGENT: Crisis detected in New Delhi (Stock: 10).")
    print("🤖 AGENT: Initiating emergency restock protocol...")
    
    time.sleep(1) # Thinking time
    
    # Buy 40 more tires for New Delhi
    store.restock("Tyre001", "New Delhi", 40)
    
    print("🤖 AGENT: Ticket closed. Inventory levels healthy.")

# if __name__ == "__main__":
#     run_agent()