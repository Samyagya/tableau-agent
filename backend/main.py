from services.inventory import InventoryStore

store = InventoryStore()
rows = store.get_by_sku("Tyre002")
print(rows)
