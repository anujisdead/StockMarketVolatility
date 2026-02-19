from flask import Flask, render_template, jsonify
import os
import markdown
import json
import logging
from scheduler import init_scheduler

# ... (logging config)

app = Flask(__name__)

from backtester import run_backtest

def load_stock_results(market='BSE'):
    """Loads the stock analysis results from JSON based on market."""
    filename = 'nse_results.json' if market == 'NSE' else 'stock_results.json'
    results_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            return json.load(f)
    return {'last_updated': 'N/A', 'results': []}

@app.route('/')
def home():
    # ... (existing home route)
    # Read the replication report to display as content
    report_content = ""
    report_path = "/Users/sreeanujnimmala/.gemini/antigravity/brain/fdf78e5c-d26b-4802-8f6a-d1d5640f846d/replication_report.md"
    
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            md_text = f.read()
            report_content = markdown.markdown(md_text, extensions=['tables'])
    else:
        report_content = "<p>Report not found.</p>"

    images = [
        {'title': 'Residuals of ARMA(2,3)', 'src': 'residuals_plot.png'},
        {'title': 'Conditional Volatility (GARCH(1,1))', 'src': 'volatility_plot.png'},
        {'title': 'Conditional Volatility (TGARCH(1,1))', 'src': 'tgarch_volatility_plot.png'}
    ]
    
    return render_template('index.html', report_content=report_content, images=images)

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

@app.route('/dashboard')
@app.route('/dashboard/<market>')
def dashboard(market='BSE'):
    market = market.upper()
    if market not in ['BSE', 'NSE']:
        market = 'BSE'
        
    data = load_stock_results(market)
    return render_template('dashboard.html', stocks=data['results'], last_updated=data['last_updated'], market=market)

@app.route('/stock/<ticker>')
def stock_detail(ticker):
    """Render the stock detail page."""
    # We can try to find basic info from the summary file first
    # Or just let the page fetch via API
    return render_template('stock_detail.html', ticker=ticker)

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    """Return historical data for chart."""
    try:
        # Load detailed JSON
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'stocks', f'{ticker}.json')
        if not os.path.exists(filepath):
            return jsonify({'error': 'Stock data not found'}), 404
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/<ticker>')
def get_backtest_data(ticker):
    results = run_backtest(ticker)
    return jsonify(results)

import feedparser
import urllib.parse

@app.route('/api/news/<ticker>')
def get_news_data(ticker):
    try:
        # Clean ticker for search (remove .BO or .NS for broader news)
        search_term = ticker.split('.')[0]
        # Encode for URL
        query = urllib.parse.quote(f"{search_term} stock finance news india")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        feed = feedparser.parse(rss_url)
        
        news_items = []
        for entry in feed.entries[:5]: # Top 5 news
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News'
            })
            
        return jsonify({'news': news_items})
    except Exception as e:
        return jsonify({'error': str(e)})

from optimizer import get_portfolio_optimization
from flask import request

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    data = request.get_json()
    tickers = data.get('tickers', [])
    if not tickers or len(tickers) < 2:
        return jsonify({'error': 'Select at least 2 stocks.'})
        
    result = get_portfolio_optimization(tickers)
    return jsonify(result)

from flask_weasyprint import HTML, render_pdf
from datetime import datetime

@app.route('/api/export/<ticker>')
def export_report(ticker):
    try:
        # Determine market and load summary data
        market = 'NSE' if ticker.endswith('.NS') else 'BSE'
        summary_file = 'nse_results.json' if market == 'NSE' else 'stock_results.json'
        summary_path = os.path.join(os.path.dirname(__file__), 'data', summary_file)
        
        stock_summary = {}
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                data = json.load(f)
                # Find the specific stock
                for s in data.get('results', []):
                    if s['ticker'] == ticker:
                        stock_summary = s
                        break
        
        if not stock_summary:
            return "Stock summary not found in analysis results", 404

        # Load detailed history for the table
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'stocks', f'{ticker}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                history = json.load(f)
                # Merge history into summary
                stock_summary.update(history)
                
        # Ensure prices exist for the table
        if 'prices' not in stock_summary:
             if 'normalized_price' in stock_summary:
                 stock_summary['prices'] = stock_summary['normalized_price']
             else:
                 stock_summary['prices'] = []
        
        # Ensure dates exist
        if 'dates' not in stock_summary:
            stock_summary['dates'] = []

        # Calculate returns if missing
        if 'returns' not in stock_summary or not stock_summary['returns']:
            prices = stock_summary.get('prices', [])
            returns = [0.0] # First day 0 return
            for i in range(1, len(prices)):
                if prices[i-1] != 0:
                    ret = (prices[i] - prices[i-1]) / prices[i-1]
                    returns.append(ret)
                else:
                    returns.append(0.0)
            stock_summary['returns'] = returns
        
        # Render PDF
        html = render_template('report_template.html', stock=stock_summary, date=datetime.now().strftime('%Y-%m-%d %H:%M'))
        return render_pdf(HTML(string=html, base_url=request.base_url), download_filename=f'{ticker}_Report.pdf')
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Initialize Scheduler
    init_scheduler(app)
    
    port = 5002
    print(f"Starting server on http://localhost:{port}")
    app.run(debug=True, port=port, use_reloader=False) # use_reloader=False prevents double execution of scheduler
