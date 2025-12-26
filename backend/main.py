from services.inventory import InventoryStore

store = InventoryStore()
# rows = store.get_by_sku("Tyre002")
# print(rows)

print("BEFORE TRANSFER")
print(store.get_by_sku("Tyre001"))

store.apply_transfer(
    sku="Tyre001",
    src="Chennai",      
    dest="New Delhi",   
    qty=20
)

print("AFTER TRANSFER")
print(store.get_by_sku("Tyre001"))
