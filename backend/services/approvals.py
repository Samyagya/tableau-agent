import uuid
from datetime import datetime
from services.inventory import InventoryStore


class ApprovalStore:
    def __init__(self):
        self.store = InventoryStore()
        self.sheet = self.store.sheet.spreadsheet.worksheet("approvals")

    def create(self, recommendation: dict):
        approval_id = str(uuid.uuid4())

        self.sheet.append_row([
            approval_id,
            recommendation["type"],
            recommendation["sku"],
            recommendation["warehouse"],
            recommendation["qty"],
            recommendation.get("from"),
            recommendation["cost"],
            "PENDING",
            "",
            "",
            datetime.utcnow().isoformat()
        ])

        return approval_id

    def approve(self, approval_id: str, user: str):
        rows = self.sheet.get_all_records()

        for idx, r in enumerate(rows, start=2):
            if r["approval_id"] == approval_id and r["status"] == "PENDING":
                self.sheet.update_cell(idx, 8, "APPROVED")
                self.sheet.update_cell(idx, 9, user)
                self.sheet.update_cell(idx, 10, datetime.utcnow().isoformat())
                return r

        return None

    def reject(self, approval_id: str, user: str):
        rows = self.sheet.get_all_records()

        for idx, r in enumerate(rows, start=2):
            if r["approval_id"] == approval_id and r["status"] == "PENDING":
                self.sheet.update_cell(idx, 8, "REJECTED")
                self.sheet.update_cell(idx, 9, user)
                self.sheet.update_cell(idx, 10, datetime.utcnow().isoformat())
                return True

        return False

    def is_approved(self, approval_id: str) -> bool:
        rows = self.sheet.get_all_records()

        for r in rows:
            if r["approval_id"] == approval_id:
                return r["status"] == "APPROVED"

        return False

