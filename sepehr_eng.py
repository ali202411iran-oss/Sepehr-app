#!/usr/bin/env python3

import os
import json
import random
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)

class DataManager:
    def __init__(self):
        self.data_file = os.path.expanduser("~/sepehr_data.json")
        self.stocks = self._load_or_create()
    
    def _load_or_create(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        data = [
            {"symbol": "FOLAD", "price": 12500, "change_24h": 2.3, "volume": 2500000},
            {"symbol": "SHSTA", "price": 8450, "change_24h": -1.2, "volume": 1800000},
            {"symbol": "KHODRO", "price": 3200, "change_24h": 4.1, "volume": 5200000},
            {"symbol": "FEMLI", "price": 18500, "change_24h": 3.4, "volume": 900000},
            {"symbol": "MADAN", "price": 6200, "change_24h": -2.8, "volume": 1200000},
            {"symbol": "SANDOGH", "price": 100500, "change_24h": 0.05, "volume": 50000},
            {"symbol": "TALA", "price": 45000, "change_24h": 0.8, "volume": 200000},
        ]
        self._save_data(data)
        return data
    
    def _save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save(self):
        self._save_data(self.stocks)
    
    def update_price(self, symbol, new_price):
        for stock in self.stocks:
            if stock['symbol'] == symbol:
                old_price = stock['price']
                stock['price'] = new_price
                stock['change_24h'] = ((new_price - old_price) / old_price) * 100
                self.save()
                return True
        return False

class SignalEngine:
    STRATEGIES = ["daily", "hourly", "ma", "custom"]
    
    def __init__(self):
        self.active = "daily"
    
    def generate(self, stock_data):
        if self.active == "daily":
            return self._daily(stock_data)
        elif self.active == "hourly":
            return self._hourly(stock_data)
        elif self.active == "ma":
            return self._ma(stock_data)
        else:
            return self._daily(stock_data)
    
    def _daily(self, data):
        change = data.get('change_24h', 0)
        volume = data.get('volume', 0)
        price = data.get('price', 0)
        if volume > 1000000 and abs(change) > 1.5:
            action = 'BUY' if change > 0 else 'SELL'
            sl = price * (0.97 if action == 'BUY' else 1.03)
            tp = price * (1.05 if action == 'BUY' else 0.95)
            return {'action': action, 'stop_loss': round(sl, 2), 'take_profit': round(tp, 2)}
        return {'action': 'HOLD', 'stop_loss': '-', 'take_profit': '-'}
    
    def _hourly(self, data):
        change = data.get('change_24h', 0) * random.uniform(0.2, 0.5)
        price = data.get('price', 0)
        if abs(change) > 1.0:
            action = 'BUY' if change > 0 else 'SELL'
            return {'action': action, 'stop_loss': round(price*0.98, 2), 'take_profit': round(price*1.03, 2)}
        return {'action': 'HOLD', 'stop_loss': '-', 'take_profit': '-'}
    
    def _ma(self, data):
        price = data.get('price', 100)
        ma_short = price * (1 + random.uniform(-0.01, 0.01))
        ma_long = price * (1 + random.uniform(-0.02, 0.02))
        if ma_short > ma_long:
            return {'action': 'BUY', 'stop_loss': round(price*0.98, 2), 'take_profit': round(price*1.05, 2)}
        elif ma_short < ma_long:
            return {'action': 'SELL', 'stop_loss': round(price*1.02, 2), 'take_profit': round(price*0.95, 2)}
        return {'action': 'HOLD', 'stop_loss': '-', 'take_profit': '-'}

class PaperTrading:
    def __init__(self):
        self.balance = 100_000_000
        self.initial_balance = 100_000_000
        self.holdings = {}
        self.trades = []
        self.total_trades = 0
        self.win_trades = 0
    
    def buy(self, symbol, price, qty):
        cost = price * qty
        if cost > self.balance:
            return False, f"INSUFFICIENT BALANCE! Need: {cost:,.0f} - Have: {self.balance:,.0f}"
        self.balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + qty
        self.trades.append({'symbol': symbol, 'action': 'BUY', 'price': price, 'qty': qty, 'time': datetime.now().strftime('%H:%M:%S')})
        self.total_trades += 1
        return True, f"BOUGHT {qty} {symbol} @ {price:,.0f}"
    
    def sell(self, symbol, price, qty=None):
        available = self.holdings.get(symbol, 0)
        if available == 0:
            return False, f"{symbol} NOT IN PORTFOLIO!"
        if qty is None or qty > available:
            qty = available
        revenue = price * qty
        self.balance += revenue
        self.holdings[symbol] -= qty
        if self.holdings[symbol] <= 0:
            del self.holdings[symbol]
        self.trades.append({'symbol': symbol, 'action': 'SELL', 'price': price, 'qty': qty, 'time': datetime.now().strftime('%H:%M:%S')})
        self.total_trades += 1
        if random.random() > 0.4:
            self.win_trades += 1
        return True, f"SOLD {qty} {symbol} @ {price:,.0f}"
    
    def status(self):
        holdings_value = 0
        for symbol, qty in self.holdings.items():
            price = random.randint(1000, 50000)
            holdings_value += price * qty
        total = self.balance + holdings_value
        profit = total - self.initial_balance
        return {
            'balance': self.balance,
            'holdings_value': holdings_value,
            'total': total,
            'profit': profit,
            'profit_percent': (profit / self.initial_balance) * 100,
            'trades': self.total_trades,
            'win_rate': (self.win_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'holdings': list(self.holdings.keys())
        }

class SepehrApp:
    def __init__(self):
        self.data = DataManager()
        self.signal = SignalEngine()
        self.paper = PaperTrading()
    
    def run(self):
        os.system('clear')
        print("="*60)
        print("SEPEHR - Trading Bot")
        print("="*60)
        print("Loaded: " + str(len(self.data.stocks)) + " symbols")
        print("Strategy: " + self.signal.active)
        print("="*60)
        
        while True:
            print("\nMENU:")
            print("1. Show stocks & signals")
            print("2. Buy (simulated)")
            print("3. Sell (simulated)")
            print("4. Portfolio status")
            print("5. Change strategy")
            print("6. Update price manually")
            print("0. Exit")
            
            choice = input("\nChoose: ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            
            elif choice == '1':
                print("\nSTOCKS & SIGNALS:")
                print("Symbol      Price       Change     Signal    SL         TP")
                print("-"*70)
                for stock in self.data.stocks:
                    sig = self.signal.generate(stock)
                    sig_color = Fore.GREEN if sig['action'] == 'BUY' else Fore.RED if sig['action'] == 'SELL' else Fore.WHITE
                    change_color = Fore.GREEN if stock['change_24h'] >= 0 else Fore.RED
                    print(f"{stock['symbol']:<12} {stock['price']:<12,} {change_color}{stock['change_24h']:>+6.2f}% {sig_color}{sig['action']:<6} {str(sig['stop_loss']):<12} {str(sig['take_profit']):<12}")
            
            elif choice == '2':
                symbols = [s['symbol'] for s in self.data.stocks]
                print("Available: " + ", ".join(symbols))
                symbol = input("Symbol: ").strip().upper()
                if symbol not in symbols:
                    print("Invalid symbol!")
                    continue
                try:
                    qty = int(input("Quantity: ").strip())
                    if qty <= 0:
                        print("Quantity must be positive!")
                        continue
                except:
                    print("Enter a number!")
                    continue
                price = next((s['price'] for s in self.data.stocks if s['symbol'] == symbol), 10000)
                ok, msg = self.paper.buy(symbol, price, qty)
                print(msg)
            
            elif choice == '3':
                if not self.paper.holdings:
                    print("No holdings!")
                    continue
                print("Holdings: " + ", ".join(self.paper.holdings.keys()))
                symbol = input("Symbol: ").strip().upper()
                if symbol not in self.paper.holdings:
                    print("Not in portfolio!")
                    continue
                price = next((s['price'] * random.uniform(0.98, 1.02) for s in self.data.stocks if s['symbol'] == symbol), 10000)
                ok, msg = self.paper.sell(symbol, price)
                print(msg)
            
            elif choice == '4':
                st = self.paper.status()
                print("\n" + "="*50)
                print("PORTFOLIO STATUS:")
                print("Balance: " + f"{st['balance']:,.0f} IRR")
                print("Stocks Value: " + f"{st['holdings_value']:,.0f} IRR")
                print("Total: " + f"{st['total']:,.0f} IRR")
                profit_color = Fore.GREEN if st['profit'] >= 0 else Fore.RED
                print(f"P/L: {st['profit']:+,.0f} IRR ({st['profit_percent']:+.2f}%)")
                print("Trades: " + str(st['trades']) + "  |  Win Rate: " + f"{st['win_rate']:.1f}%")
                print("Holdings: " + (", ".join(st['holdings']) if st['holdings'] else "None"))
                print("="*50)
            
            elif choice == '5':
                print("\nSTRATEGIES:")
                for i, s in enumerate(self.signal.STRATEGIES, 1):
                    print(str(i) + ". " + s)
                try:
                    sel = int(input("Choose: ").strip()) - 1
                    if 0 <= sel < len(self.signal.STRATEGIES):
                        self.signal.active = self.signal.STRATEGIES[sel]
                        print("Strategy changed to " + self.signal.active)
                    else:
                        print("Invalid!")
                except:
                    print("Enter a number!")
            
            elif choice == '6':
                symbol = input("Symbol: ").strip().upper()
                if symbol not in [s['symbol'] for s in self.data.stocks]:
                    print("Invalid symbol!")
                    continue
                try:
                    new_price = int(input("New Price: ").strip())
                    if new_price <= 0:
                        print("Price must be positive!")
                        continue
                except:
                    print("Enter a number!")
                    continue
                if self.data.update_price(symbol, new_price):
                    print(f"{symbol} price updated to {new_price:,}")
                else:
                    print("Update failed!")
            
            else:
                print("Invalid choice!")

if __name__ == "__main__":
    app = SepehrApp()
    app.run()
