import uuid
from datetime import datetime
from services.inventory import InventoryStore


class ExecutionLogger:
    def __init__(self):
        self.store = InventoryStore()
        self.sheet = self.store.sheet.spreadsheet.worksheet("executions")

    def log(self, approval_id, action, sku, warehouse, qty, source=None, result="SUCCESS"):
        self.sheet.append_row([
            str(uuid.uuid4()),
            approval_id,
            action,
            sku,
            warehouse,
            qty,
            source,
            datetime.utcnow().isoformat(),
            result
        ])
