import uuid
import datetime
import random

# ----- User Module -----
class User:
    def __init__(self, name, country, biometric=True):
        self.name = name
        self.country = country
        self.biometric_verified = biometric
        self.wallet = Wallet(owner=self)
        self.card = TokenizedCard(owner=self)

# ----- Wallet Module -----
class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.balances = {'USD': 0.0, 'TRY': 0.0, 'IRR': 0.0}
        self.ledger = []

    def deposit(self, currency, amount):
        self.balances[currency] += amount

    def show_balances(self):
        print(f"\n💼 Wallet for {self.owner.name} ({self.owner.country})")
        for c, amt in self.balances.items():
            print(f"   {c}: {amt:,.2f}")
        print("────────────────────────────")

    def log_transaction(self, entry):
        self.ledger.append(entry)

# ----- Tokenized Card Module -----
class TokenizedCard:
    def __init__(self, owner):
        self.owner = owner

    def generate_card(self):
        pan = "5313 " + " ".join(["%04d" % random.randint(0, 9999) for _ in range(3)])
        cvv = random.randint(100, 999)
        return {"pan": pan, "cvv": cvv, "token": str(uuid.uuid4()).split('-')[0].upper()}

# ----- FX Engine -----
class FXEngine:
    fx_table = {
        ('USD', 'TRY'): 32.5,
        ('USD', 'IRR'): 580000,
        ('TRY', 'USD'): 1/32.5,
        ('IRR', 'USD'): 1/580000
    }

    @staticmethod
    def convert(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount, 1.0
        rate = FXEngine.fx_table.get((from_currency, to_currency))
        if not rate:
            raise Exception("FX rate not available")
        return amount * rate, rate

# ----- POS Simulation -----
class MerchantPOS:
    def __init__(self, merchant_name, accepted_currency='USD'):
        self.name = merchant_name
        self.accepted_currency = accepted_currency

    def accept_payment(self, user, amount, currency):
        print(f"\n🧾 {self.name} | Accepting Payment")
        print(f"User: {user.name}")
        print(f"Biometric Verification... {'✅' if user.biometric_verified else '❌'}")
        token_info = user.card.generate_card()
        print(f"Tokenized Card: {token_info['pan']} | CVV: {token_info['cvv']} | Token: {token_info['token']}")
        
        if user.wallet.balances[currency] < amount:
            print(f"❌ Insufficient funds in {currency}")
            return
        
        user.wallet.balances[currency] -= amount
        tx_id = str(uuid.uuid4()).split('-')[0].upper()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user.wallet.log_transaction({
            'type': 'Purchase',
            'merchant': self.name,
            'amount': amount,
            'currency': currency,
            'tx_id': tx_id,
            'time': timestamp
        })

        print(f"✅ Payment of {amount:.2f} {currency} approved")
        print(f"🕒 TX ID: {tx_id} | Time: {timestamp}")
        print("────────────────────────────")

# ----- Simulate DevPay Ecosystem -----
if __name__ == "__main__":
    print("🚀 DevPay Ecosystem Simulation Start")

    # Create users
    ali = User("Ali", "Iran")
    sara = User("Sara", "Türkiye")

    # Initial deposits
    ali.wallet.deposit("IRR", 3_000_000)
    sara.wallet.deposit("TRY", 2_000)

    # Show initial balances
    ali.wallet.show_balances()
    sara.wallet.show_balances()

    # FX conversion & transfer from Sara to Ali
    usd_amount, rate = FXEngine.convert(500, 'TRY', 'USD')
    ali.wallet.deposit('USD', usd_amount)
    sara.wallet.balances['TRY'] -= 500

    print(f"\n🌍 FX Transfer: Sara ➡️ Ali")
    print(f"   Converted 500 TRY → {usd_amount:.2f} USD @ Rate {rate:.2f}")
    print("────────────────────────────")

    # Ali attempts a merchant payment
    pos = MerchantPOS("Café Istanbul", accepted_currency='USD')
    pos.accept_payment(ali, 20, 'USD')

    # Show final balances
    ali.wallet.show_balances()
    sara.wallet.show_balances()
