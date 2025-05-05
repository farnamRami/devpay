import uuid
import datetime
import random

# User Entity
class User:
    def __init__(self, name, country, biometric=True):
        self.name = name
        self.country = country
        self.biometric_verified = biometric
        self.wallet = Wallet(owner=self)
        self.card = TokenizedCard(owner=self)
        self.kyc_verified = True
        self.user_id = str(uuid.uuid4()).split('-')[0]

# Wallet System
class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.balances = {'USD': 0.0, 'TRY': 0.0, 'IRR': 0.0}
        self.ledger = []

    def deposit(self, currency, amount):
        self.balances[currency] += amount

    def withdraw(self, currency, amount):
        if self.balances[currency] >= amount:
            self.balances[currency] -= amount
            return True
        return False

    def show_balances(self):
        print(f"\n💼 Wallet for {self.owner.name} ({self.owner.country})")
        for c, amt in self.balances.items():
            print(f"   {c}: {amt:,.2f}")
        print("────────────────────────────────────")

    def log_transaction(self, entry):
        self.ledger.append(entry)

    def show_ledger(self):
        print(f"\n📜 Ledger – {self.owner.name}")
        for entry in self.ledger:
            line = f"{entry['time']} | {entry['type']} | {entry['amount']:,.2f} {entry['currency']} | {entry['info']}"
            print(line)
        print("────────────────────────────────────")

# Tokenization System
class TokenizedCard:
    def __init__(self, owner):
        self.owner = owner

    def generate_token(self):
        pan = "5313 " + " ".join(["%04d" % random.randint(0, 9999) for _ in range(3)])
        cvv = random.randint(100, 999)
        token = str(uuid.uuid4()).split('-')[0].upper()
        return {"pan": pan, "cvv": cvv, "token": token}

# FX Engine
class FXEngine:
    fx_table = {
        ('USD', 'TRY'): 38.5,
        ('USD', 'IRR'): 900000,
        ('TRY', 'USD'): 1/38.5,
        ('IRR', 'USD'): 1/900000,
        ('TRY', 'IRR'): 900000 / 38.5,
        ('IRR', 'TRY'): 38.5 / 900000
    }

    @staticmethod
    def convert(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount, 1.0
        rate = FXEngine.fx_table.get((from_currency, to_currency))
        if not rate:
            raise Exception("Currency pair unsupported.")
        return amount * rate, rate

# SoftPOS Merchant System
class MerchantPOS:
    def __init__(self, name, accepted_currency='USD'):
        self.name = name
        self.accepted_currency = accepted_currency
        self.merchant_id = str(uuid.uuid4()).split('-')[0]

    def process_payment(self, user, amount, currency):
        print(f"\n🧾 Payment to {self.name} [{self.merchant_id}]")
        print(f"👤 Customer: {user.name} | Biometric: {'✅' if user.biometric_verified else '❌'}")

        token = user.card.generate_token()
        print(f"💳 Tokenized Card: {token['pan']} | CVV: {token['cvv']} | Token: {token['token']}")

        if not user.wallet.withdraw(currency, amount):
            print(f"❌ Declined: Not enough balance in {currency}")
            return

        tx_id = str(uuid.uuid4()).split('-')[0].upper()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user.wallet.log_transaction({
            'type': 'POS Purchase',
            'amount': amount,
            'currency': currency,
            'time': timestamp,
            'info': f"{self.name} | TX ID: {tx_id}"
        })

        print(f"✅ Approved: {amount:.2f} {currency} | TX ID: {tx_id}")
        print("────────────────────────────────────")

# Cross-Border FX Transfer
def cross_border_transfer(sender, receiver, amount, from_currency, to_currency):
    print(f"\n🌐 FX Transfer – {sender.name} ➡️ {receiver.name}")
    converted_amount, rate = FXEngine.convert(amount, from_currency, to_currency)

    if not sender.wallet.withdraw(from_currency, amount):
        print("❌ Failed: Insufficient balance.")
        return

    receiver.wallet.deposit(to_currency, converted_amount)
    tx_id = str(uuid.uuid4()).split('-')[0].upper()
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sender.wallet.log_transaction({
        'type': 'Send FX',
        'amount': amount,
        'currency': from_currency,
        'time': time_now,
        'info': f"To {receiver.name} | Rate {rate:.2f} | TX: {tx_id}"
    })
    receiver.wallet.log_transaction({
        'type': 'Receive FX',
        'amount': converted_amount,
        'currency': to_currency,
        'time': time_now,
        'info': f"From {sender.name} | Rate {rate:.2f} | TX: {tx_id}"
    })

    print(f"💱 Sent {amount:.2f} {from_currency} → Received {converted_amount:.2f} {to_currency}")
    print(f"✔️ Rate: {rate:.2f} | TX ID: {tx_id}")
    print("────────────────────────────────────")

# Run Simulation
if __name__ == "__main__":
    print("🚀 DevPay Ecosystem Simulation Start\n")

    # Users and Merchant Setup
    ali = User("Ali", "Iran")
    sara = User("Sara", "Türkiye")
    merchant = MerchantPOS("Global Electronics", accepted_currency='USD')

    # Initial Balances
    ali.wallet.deposit("IRR", 5_000_000)
    sara.wallet.deposit("TRY", 3_000)

    ali.wallet.show_balances()
    sara.wallet.show_balances()

    # Cross-Border Transfer: Sara → Ali
    cross_border_transfer(sara, ali, 1500, 'TRY', 'USD')

    # Ali makes a merchant payment
    merchant.process_payment(ali, 40, 'USD')

    # Final Wallet Status
    ali.wallet.show_balances()
    sara.wallet.show_balances()

    # Ledger Review
    ali.wallet.show_ledger()
    sara.wallet.show_ledger()
