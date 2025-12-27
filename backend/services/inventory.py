import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()


class InventoryStore:

    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=scopes
        )

        client = gspread.authorize(creds)

        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            raise Exception("SPREADSHEET_ID not set in .env file")

        self.sheet = client.open_by_key(spreadsheet_id).worksheet("inventory")

    # getting records from google sheets (read access)
    def get_all_inventory(self):
        return self.sheet.get_all_records()
    
    def get_by_sku(self, sku):
        rows = self.sheet.get_all_records()
        return [r for r in rows if r["SKU"] == sku]

    def get_qty(self, sku, warehouse):  
        rows = self.sheet.get_all_records()

        for r in rows:
            if r["SKU"] == sku and r["Warehouse"] == warehouse:
                try:
                    return int(r["Qty"])
                except ValueError:
                    return 0

        return 0

    # apply transfer (write access)
    def restock(self, sku, warehouse, amount):
        rows = self.sheet.get_all_records()

        for idx, r in enumerate(rows, start=2):  # row 1 = headers
            if r["SKU"] == sku and r["Warehouse"] == warehouse:
                current_qty = int(r["Qty"])
                new_qty = current_qty + amount

                self.sheet.update_cell(idx, 3, new_qty)

                print(
                    f"SUCCESS: Restocked {amount} units of {sku} in {warehouse}. "
                    f"New Qty: {new_qty}"
                )
                return new_qty

        print(f"ERROR: Could not find {sku} in {warehouse}")
        return None

    def transfer(self, sku, src_warehouse, dest_warehouse, qty):
        rows = self.sheet.get_all_records()

        src_row = None
        dest_row = None

        for idx, r in enumerate(rows, start=2):
            if r["SKU"] == sku and r["Warehouse"] == src_warehouse:
                src_row = (idx, r)
            if r["SKU"] == sku and r["Warehouse"] == dest_warehouse:
                dest_row = (idx, r)

        if not src_row or not dest_row:
            raise Exception("Invalid SKU or warehouse for transfer")

        src_qty = int(src_row[1]["Qty"])
        dest_qty = int(dest_row[1]["Qty"])

        if src_qty < qty:
            raise Exception(
                f"Insufficient stock at {src_warehouse} "
                f"(Available: {src_qty}, Required: {qty})"
            )

        # Perform updates
        self.sheet.update_cell(src_row[0], 3, src_qty - qty)
        self.sheet.update_cell(dest_row[0], 3, dest_qty + qty)

        print(
            f"SUCCESS: Transferred {qty} units of {sku} "
            f"from {src_warehouse} → {dest_warehouse}"
        )
