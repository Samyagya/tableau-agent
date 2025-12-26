import gspread
from google.oauth2.service_account import Credentials

import os
from dotenv import load_dotenv

load_dotenv()

class InventoryStore:

    # class initializer
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=scopes
        )

        client = gspread.authorize(creds)
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.sheet = client.open_by_key(spreadsheet_id).worksheet("inventory")

#getting records from google sheets (read access)
    def get_by_sku(self, sku):
        rows = self.sheet.get_all_records()
        return [r for r in rows if r["SKU"] == sku]

#apply transfer (write access)
    def apply_transfer(self, sku, src, dest, qty):
        rows = self.sheet.get_all_records()

        src_row = None
        dest_row = None

        for idx, r in enumerate(rows, start=2):  # start=2 because row 1 = headers
            if r["SKU"] == sku and r["Warehouse"] == src:
                src_row = (idx, r)
            if r["SKU"] == sku and r["Warehouse"] == dest:
                dest_row = (idx, r)

        if not src_row or not dest_row:
            raise Exception("Invalid warehouse or SKU")

        if src_row[1]["Qty"] < qty:
            raise Exception("Insufficient stock at source")

        # update cells
        self.sheet.update_cell(src_row[0], 3, src_row[1]["Qty"] - qty)
        self.sheet.update_cell(dest_row[0], 3, dest_row[1]["Qty"] + qty)

