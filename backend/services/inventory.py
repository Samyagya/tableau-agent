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
        self.sheet = client.open_by_key(spreadsheet_id).worksheet("inventory")

    def get_by_sku(self, sku):
        rows = self.sheet.get_all_records()
        return [r for r in rows if r["SKU"] == sku]
