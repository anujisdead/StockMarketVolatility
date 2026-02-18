from flask import Flask, render_template, jsonify
import os
import markdown
import json
import logging
from scheduler import init_scheduler

# ... (logging config)

app = Flask(__name__)

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
    stock_path = os.path.join(os.path.dirname(__file__), 'data', 'stocks', f'{ticker}.json')
    if os.path.exists(stock_path):
        with open(stock_path, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    else:
        return jsonify({'error': 'Stock data not found', 'ticker': ticker}), 404

if __name__ == '__main__':
    # Initialize Scheduler
    init_scheduler(app)
    
    port = 5002
    print(f"Starting server on http://localhost:{port}")
    app.run(debug=True, port=port, use_reloader=False) # use_reloader=False prevents double execution of scheduler
