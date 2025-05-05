import uuid
import datetime
import time

class DevPayWallet:
    def __init__(self, user_name, currency='IRR', balance=0):
        self.user_name = user_name
        self.currency = currency
        self.balance = balance
        self.ledger = []

    def show_balance(self):
        print(f"💼 Wallet - {self.user_name}")
        print(f"   Balance: {self.balance:,} {self.currency}")
        print("   -----------------------------")

    def transfer(self, amount, recipient_wallet):
        print(f"\n🔄 Initiating Transfer: {self.user_name} ➡️ {recipient_wallet.user_name}")
        print(f"   Amount: {amount:,} {self.currency}")
        print(f"   Biometric Authentication... ✅")
        print(f"   Tokenizing Card... 🔐")

        if amount > self.balance:
            print(f"   ❌ ERROR: Insufficient funds in {self.user_name}'s wallet.\n")
            return

        self.balance -= amount
        recipient_wallet.balance += amount

        tx_id = str(uuid.uuid4()).split('-')[0].upper()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.ledger.append({
            'type': 'Sent',
            'to': recipient_wallet.user_name,
            'amount': amount,
            'tx_id': tx_id,
            'time': timestamp
        })

        recipient_wallet.ledger.append({
            'type': 'Received',
            'from': self.user_name,
            'amount': amount,
            'tx_id': tx_id,
            'time': timestamp
        })

        time.sleep(1)
        print(f"   ✅ Transfer Successful!")
        print(f"   🔐 Tokenized TX ID: {tx_id}")
        print(f"   🕒 Time: {timestamp}")
        print(f"   --------------------------------\n")

    def show_ledger(self):
        print(f"\n📒 Ledger for {self.user_name}")
        print("   --------------------------------")
        for entry in self.ledger:
            if entry['type'] == 'Sent':
                print(f"   ➖ Sent {entry['amount']:,} {self.currency} to {entry['to']} | TX: {entry['tx_id']}")
            else:
                print(f"   ➕ Received {entry['amount']:,} {self.currency} from {entry['from']} | TX: {entry['tx_id']}")
        print("   --------------------------------\n")


# === DEMO: Simulate Real Use ===

print("🚀 Welcome to DevPay Demo\n")
ali = DevPayWallet("Ali", balance=120000)
sara = DevPayWallet("Sara", balance=80000)

# Show initial state
ali.show_balance()
sara.show_balance()

# Simulate transfer
ali.transfer(30000, sara)

# Show final state
ali.show_balance()
sara.show_balance()

# Show detailed ledgers
ali.show_ledger()
sara.show_ledger()
