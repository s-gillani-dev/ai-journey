# inspect_db.py
import json
import os
from tabulate import tabulate # You may need to: pip install tabulate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DB_PATH = os.path.join(BASE_DIR, "session_store.json")

def view_database():
    if not os.path.exists(STATE_DB_PATH):
        print("❌ No database file found yet. Place an order first!")
        return

    with open(STATE_DB_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Database file is empty or corrupted.")
            return

    print("\n" + "="*80)
    print(f"       📊 DineFlow SESSION DATABASE ({len(data)} Sessions Found)")
    print("="*80)

    table_data = []
    for sess_id, state in data.items():
        # Format the cart for better readability
        cart = state.get("cart", {})
        cart_str = ", ".join([f"{qty}x {sku}" for sku, qty in cart.items()]) if cart else "Empty"
        
        table_data.append([
            sess_id,
            state.get("user_id", "N/A"),
            state.get("active_agent", "N/A"),
            f"{state.get('tool_budget_remaining', 0)}/5",
            state.get("order_status", "N/A"),
            cart_str
        ])

    headers = ["Session ID", "User", "Current Agent", "Budget", "Status", "Cart Content"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("="*80 + "\n")

if __name__ == "__main__":
    view_database()