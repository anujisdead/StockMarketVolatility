"""
Paper Trading Engine
Manages a virtual portfolio with simulated buy/sell orders using real market data.
All state is stored in a local JSON file — no database or heavy dependencies needed.
"""

import json
import os
from datetime import datetime

# File path for persistent storage
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'paper_portfolio.json')

DEFAULT_PORTFOLIO = {
    'cash': 1000000.00,         # Starting capital: ₹10,00,000
    'initial_capital': 1000000.00,
    'positions': {},            # { ticker: { qty, avg_price, market } }
    'trade_history': [],        # List of all executed trades
    'created_at': None,
}


def _load_portfolio():
    """Load portfolio from disk, or create a fresh one."""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return _reset_portfolio()


def _save_portfolio(portfolio):
    """Persist portfolio to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def _reset_portfolio():
    """Create a brand-new portfolio."""
    portfolio = dict(DEFAULT_PORTFOLIO)
    portfolio['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    portfolio['positions'] = {}
    portfolio['trade_history'] = []
    _save_portfolio(portfolio)
    return portfolio


def _get_stock_price(ticker):
    """
    Get latest price from the pre-analyzed stock results (no API calls).
    Falls back to per-stock JSON files.
    """
    # Try summary files first (fast)
    for filename in ['stock_results.json', 'nse_results.json']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                for stock in data.get('results', []):
                    if stock['ticker'] == ticker:
                        return stock.get('last_price', 0)

    # Fallback: per-stock JSON
    stock_file = os.path.join(DATA_DIR, 'stocks', f'{ticker}.json')
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            data = json.load(f)
            prices = data.get('prices', data.get('normalized_price', []))
            if prices:
                return prices[-1]

    return 0


def get_portfolio_summary():
    """
    Returns full portfolio state with current valuations.
    """
    portfolio = _load_portfolio()

    positions_with_value = []
    total_invested = 0
    total_current_value = 0

    for ticker, pos in portfolio['positions'].items():
        current_price = _get_stock_price(ticker)
        qty = pos['qty']
        avg_price = pos['avg_price']
        invested = qty * avg_price
        current_val = qty * current_price
        pnl = current_val - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0

        total_invested += invested
        total_current_value += current_val

        positions_with_value.append({
            'ticker': ticker,
            'qty': qty,
            'avg_price': round(avg_price, 2),
            'current_price': round(current_price, 2),
            'invested': round(invested, 2),
            'current_value': round(current_val, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': round(pnl_pct, 2),
            'market': pos.get('market', 'BSE'),
        })

    # Sort by current value descending
    positions_with_value.sort(key=lambda x: x['current_value'], reverse=True)

    portfolio_value = portfolio['cash'] + total_current_value
    total_pnl = portfolio_value - portfolio['initial_capital']
    total_pnl_pct = (total_pnl / portfolio['initial_capital'] * 100)

    return {
        'cash': round(portfolio['cash'], 2),
        'initial_capital': portfolio['initial_capital'],
        'portfolio_value': round(portfolio_value, 2),
        'total_invested': round(total_invested, 2),
        'total_current_value': round(total_current_value, 2),
        'total_pnl': round(total_pnl, 2),
        'total_pnl_pct': round(total_pnl_pct, 2),
        'positions': positions_with_value,
        'trade_count': len(portfolio['trade_history']),
        'created_at': portfolio.get('created_at', 'N/A'),
    }


def get_trade_history():
    """Returns the full trade ledger."""
    portfolio = _load_portfolio()
    # Return in reverse chronological order
    return list(reversed(portfolio['trade_history']))


def execute_trade(ticker, action, qty):
    """
    Execute a paper trade.
    action: 'BUY' or 'SELL'
    Returns: dict with success/error and trade details
    """
    portfolio = _load_portfolio()
    price = _get_stock_price(ticker)

    if price <= 0:
        return {'error': f'No price data found for {ticker}. Ensure analysis has been run.'}

    qty = int(qty)
    if qty <= 0:
        return {'error': 'Quantity must be positive.'}

    # Determine market from ticker suffix
    market = 'NSE' if ticker.endswith('.NS') else 'BSE'

    if action == 'BUY':
        cost = price * qty
        if cost > portfolio['cash']:
            max_qty = int(portfolio['cash'] // price)
            return {'error': f'Insufficient funds. You can buy max {max_qty} shares (₹{round(portfolio["cash"], 2)} available).'}

        portfolio['cash'] -= cost

        # Update or create position
        if ticker in portfolio['positions']:
            existing = portfolio['positions'][ticker]
            total_qty = existing['qty'] + qty
            total_cost = (existing['qty'] * existing['avg_price']) + cost
            existing['avg_price'] = total_cost / total_qty
            existing['qty'] = total_qty
        else:
            portfolio['positions'][ticker] = {
                'qty': qty,
                'avg_price': price,
                'market': market,
            }

    elif action == 'SELL':
        if ticker not in portfolio['positions']:
            return {'error': f'No position in {ticker} to sell.'}

        pos = portfolio['positions'][ticker]
        if qty > pos['qty']:
            return {'error': f'You only hold {pos["qty"]} shares of {ticker}.'}

        proceeds = price * qty
        portfolio['cash'] += proceeds

        pos['qty'] -= qty
        if pos['qty'] == 0:
            del portfolio['positions'][ticker]

    else:
        return {'error': f'Invalid action: {action}. Use BUY or SELL.'}

    # Record trade
    trade_record = {
        'ticker': ticker,
        'action': action,
        'qty': qty,
        'price': round(price, 2),
        'total': round(price * qty, 2),
        'market': market,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    portfolio['trade_history'].append(trade_record)

    _save_portfolio(portfolio)

    return {
        'success': True,
        'trade': trade_record,
        'cash_remaining': round(portfolio['cash'], 2),
    }


def reset_portfolio():
    """Wipe the portfolio and start fresh."""
    _reset_portfolio()
    return {'success': True, 'message': 'Portfolio reset to ₹10,00,000.'}


def get_available_stocks():
    """
    Returns a combined, deduplicated list of all stocks available for trading.
    """
    all_stocks = []
    seen = set()

    for filename in ['stock_results.json', 'nse_results.json']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                for stock in data.get('results', []):
                    t = stock['ticker']
                    if t not in seen:
                        seen.add(t)
                        all_stocks.append({
                            'ticker': t,
                            'price': round(stock.get('last_price', 0), 2),
                            'signal': stock.get('signal', 'N/A'),
                            'volatility': round(stock.get('current_volatility', 0), 4),
                            'market': 'NSE' if t.endswith('.NS') else 'BSE',
                        })

    all_stocks.sort(key=lambda x: x['ticker'])
    return all_stocks
