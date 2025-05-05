import uuid
import datetime
import random

# -------------------- User --------------------
class User:
    def __init__(self, name, country, national_id):
        self.name = name
        self.country = country
        self.national_id = national_id
        self.user_id = str(uuid.uuid4()).split('-')[0]
        self.kyc_verified = False
        self.biometric_verified = False
        self.wallet = Wallet(self)
        self.card = TokenizedCard(self)

    def run_ekyc(self):
        print(f"🔍 Running eKYC for {self.name} ({self.country})...")
        if len(self.national_id) >= 8:
            self.kyc_verified = True
            self.biometric_verified = True
            print(f"✅ KYC passed. Biometric verified.\n")
        else:
            print(f"❌ KYC failed for {self.name}.")
            return False
        return True

# -------------------- Wallet --------------------
class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.balances = {'USD': 0.0, 'TRY': 0.0, 'IRR': 0.0}
        self.ledger = []

    def deposit(self, currency, amount, source="System"):
        self.balances[currency] += amount
        self._log("Deposit", amount, currency, f"From {source}")

    def withdraw(self, currency, amount):
        if self.balances.get(currency, 0) >= amount:
            self.balances[currency] -= amount
            return True
        return False

    def show_balances(self):
        print(f"\n💼 Wallet – {self.owner.name}")
        for cur, amt in self.balances.items():
            print(f"   {cur}: {amt:,.2f}")
        print("────────────────────────────────")

    def _log(self, tx_type, amount, currency, info):
        tx_id = str(uuid.uuid4()).split('-')[0].upper()
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ledger.append({
            'time': time_now,
            'type': tx_type,
            'amount': amount,
            'currency': currency,
            'info': f"{info} | TX: {tx_id}"
        })

    def show_ledger(self):
        print(f"\n📜 Transaction History – {self.owner.name}")
        for entry in self.ledger:
            print(f"{entry['time']} | {entry['type']} | {entry['amount']:,.2f} {entry['currency']} | {entry['info']}")
        print("────────────────────────────────")

# -------------------- Card --------------------
class TokenizedCard:
    def __init__(self, owner):
        self.owner = owner

    def generate(self):
        pan = "5313 " + " ".join(["%04d" % random.randint(0, 9999) for _ in range(3)])
        cvv = random.randint(100, 999)
        token = str(uuid.uuid4()).split('-')[0].upper()
        return {"pan": pan, "cvv": cvv, "token": token}

# -------------------- FX --------------------
class FXEngine:
    fx_rates = {
        ('USD', 'TRY'): 32.5,
        ('TRY', 'USD'): 1 / 32.5,
        ('USD', 'IRR'): 580000,
        ('IRR', 'USD'): 1 / 580000,
        ('TRY', 'IRR'): 580000 / 32.5,
        ('IRR', 'TRY'): 32.5 / 580000
    }

    @staticmethod
    def convert(amount, from_cur, to_cur):
        if from_cur == to_cur:
            return amount, 1.0
        key = (from_cur, to_cur)
        rate = FXEngine.fx_rates.get(key)
        if not rate:
            raise Exception("Currency pair not supported.")
        return amount * rate, rate

# -------------------- POS --------------------
class MerchantPOS:
    def __init__(self, name, accepted_currency='USD'):
        self.name = name
        self.merchant_id = str(uuid.uuid4()).split('-')[0]
        self.accepted_currency = accepted_currency

    def accept_payment(self, user, amount, currency):
        print(f"\n🧾 {self.name} [Merchant ID: {self.merchant_id}]")
        print(f"👤 {user.name} | Biometric: {'✅' if user.biometric_verified else '❌'}")

        if not user.biometric_verified:
            print("❌ Payment failed: biometric not verified.")
            return

        confirm = input(f"Confirm payment of {amount:.2f} {currency} at {self.name}? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("❌ Transaction cancelled by user.")
            return

        card = user.card.generate()
        print(f"💳 Tokenized Card: {card['pan']} | CVV: {card['cvv']} | TX Token: {card['token']}")

        if not user.wallet.withdraw(currency, amount):
            print(f"❌ Declined: insufficient funds in {currency}")
            return

        user.wallet._log("POS Purchase", amount, currency, f"To {self.name}")
        print(f"✅ Approved: {amount:.2f} {currency} at {self.name}")
        print("────────────────────────────────")

# -------------------- FX Transfer --------------------
def cross_border_transfer(sender, receiver, amount, from_currency, to_currency):
    print(f"\n🌐 FX Transfer from {sender.name} ➡️ {receiver.name}")
    converted, rate = FXEngine.convert(amount, from_currency, to_currency)

    confirm = input(f"Confirm transfer of {amount:.2f} {from_currency} to {receiver.name}? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("❌ Transfer cancelled by user.")
        return

    if not sender.wallet.withdraw(from_currency, amount):
        print("❌ Transfer failed: insufficient funds.")
        return

    receiver.wallet.deposit(to_currency, converted, source=sender.name)
    sender.wallet._log("FX Send", amount, from_currency, f"To {receiver.name} @ Rate {rate:.2f}")
    receiver.wallet._log("FX Receive", converted, to_currency, f"From {sender.name} @ Rate {rate:.2f}")

    print(f"💱 {amount:.2f} {from_currency} → {converted:.2f} {to_currency} @ Rate {rate:.2f}")
    print("────────────────────────────────")

# -------------------- Main Simulation --------------------
def run_interactive_simulation():
    print("🚀 DevPay Interactive Ecosystem Simulation\n")

    ali = User("Ali", "Iran", national_id="IR87654321")
    sara = User("Sara", "Türkiye", national_id="TR12345678")

    if not (ali.run_ekyc() and sara.run_ekyc()):
        return

    ali.wallet.deposit("IRR", 5_000_000, source="CBI Disbursement")
    sara.wallet.deposit("TRY", 3_000, source="Payroll")

    ali.wallet.show_balances()
    sara.wallet.show_balances()

    cross_border_transfer(sara, ali, 1500, "TRY", "USD")

    merchant = MerchantPOS("Smart Bazaar")
    merchant.accept_payment(ali, 40, "USD")

    ali.wallet.show_balances()
    sara.wallet.show_balances()
    ali.wallet.show_ledger()
    sara.wallet.show_ledger()

# Start simulation
run_interactive_simulation()
