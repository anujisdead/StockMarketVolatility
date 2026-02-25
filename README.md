# 📈 Stock Market Volatility Analyzer

A full-stack Python application for analyzing stock market volatility using **GARCH family models** (GARCH, TGARCH, ARCH) and **ARMA** on BSE and NSE listed stocks. Features a Flask web dashboard with interactive charts, a volatility-based backtesting engine, stock screener, portfolio optimizer, and PDF report export.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Volatility Modeling** | ARMA(2,3), ARCH(1), GARCH(1,1), TGARCH(1,1) models on historical returns |
| **BSE & NSE Analysis** | Automated analysis pipelines for both Indian stock exchanges |
| **Trading Signals** | Buy / Sell / Hold / Caution signals based on forecast vs. current volatility |
| **Interactive Dashboard** | Flask web app with per-stock detail pages and interactive charts |
| **Backtesting Engine** | Volatility-based strategy backtester with equity curve comparison against Buy & Hold |
| **Stock Screener** | Filter stocks by signal type, max volatility (interday & intraday modes) |
| **Portfolio Optimizer** | Mean-variance portfolio optimization for selected stocks |
| **PDF Export** | Export detailed per-stock analysis reports as PDF |
| **Real-time Feed** | Live price & volatility updates via Redis pub/sub + WebSockets |
| **News Feed** | Google News RSS integration for per-stock financial news |

---

## 🗂️ Project Structure

```
StockMarketVolatility/
├── README.md
├── requirements.txt
├── run_daily.sh              # Shell script for scheduled daily analysis
├── src/
│   ├── web_app.py            # Flask web application (main entry point)
│   ├── models.py             # ARMA, GARCH, TGARCH model fitting & analysis
│   ├── strategy.py           # Trading signal generation logic
│   ├── backtester.py         # Volatility-based backtesting engine
│   ├── optimizer.py          # Portfolio optimization (mean-variance)
│   ├── scheduler.py          # APScheduler for periodic re-analysis
│   ├── data_loader.py        # Sensex data loader (for research scripts)
│   ├── stock_data_loader.py  # Stock data fetcher via yfinance
│   ├── price_engine.py       # Real-time price streaming engine
│   ├── run_stock_analysis.py # BSE analysis pipeline
│   ├── run_nse_analysis.py   # NSE analysis pipeline
│   ├── run_garch.py          # Standalone GARCH analysis script
│   ├── run_arma.py           # Standalone ARMA analysis script
│   ├── run_tgarch.py         # Standalone TGARCH analysis script
│   ├── run_analysis.py       # General analysis runner
│   ├── config/
│   │   ├── stocks.json       # BSE stock tickers configuration
│   │   └── nse_stocks.json   # NSE stock tickers configuration
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── stock_detail.html
│   │   ├── screener.html
│   │   ├── methodology.html
│   │   └── report_template.html
│   ├── static/               # Static assets (CSS, JS, images)
│   └── data/                 # Generated analysis data (JSON files)
│       └── stocks/           # Per-stock detailed data
└── venv/                     # Python virtual environment
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Redis** (optional — only needed for real-time intraday price feeds)

### 1. Clone the Repository

```bash
git clone https://github.com/anujisdead/StockMarketVolatility.git
cd StockMarketVolatility
```

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

You will also need these additional packages for full functionality:

```bash
pip install flask-socketio eventlet flask-weasyprint redis markdown
```

### 4. Run Stock Analysis (Generate Data)

Before launching the web app, run the analysis pipelines to generate the data files:

```bash
# BSE Stocks
python src/run_stock_analysis.py

# NSE Stocks
python src/run_nse_analysis.py
```

This fetches 10 years of historical data via **yfinance**, fits GARCH models, generates trading signals, and saves results to `src/data/`.

### 5. Launch the Web Application

```bash
python src/web_app.py
```

Open your browser and navigate to: **http://localhost:5002**

---

## 📖 Usage Guide

### Web Dashboard Pages

| Route | Page | Description |
|---|---|---|
| `/` | **Home** | Research report with ARMA/GARCH/TGARCH volatility plots |
| `/dashboard` | **BSE Dashboard** | All BSE stocks with signals, volatility, and prices |
| `/dashboard/NSE` | **NSE Dashboard** | All NSE stocks with signals, volatility, and prices |
| `/stock/<ticker>` | **Stock Detail** | Interactive chart, backtest results, news, and PDF export for a specific stock |
| `/screener` | **Screener** | Filter stocks by signal type and volatility thresholds |
| `/methodology` | **Methodology** | Explanation of models and signal generation logic |

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/stock/<ticker>` | GET | Historical price & volatility data (JSON) |
| `/api/backtest/<ticker>` | GET | Run backtest and return performance metrics |
| `/api/news/<ticker>` | GET | Latest financial news for a stock |
| `/api/optimize` | POST | Portfolio optimization (send `{"tickers": [...]}`) |
| `/api/export/<ticker>` | GET | Download PDF report for a stock |
| `/api/screener` | POST | Filter stocks with custom criteria |

### Standalone Model Scripts

Run individual volatility models on Sensex data:

```bash
python src/run_garch.py    # ARMA(2,3) → ARCH(1) → GARCH(1,1)
python src/run_arma.py     # ARMA model fitting
python src/run_tgarch.py   # TGARCH(1,1) for leverage effects
```

### Configuring Stocks

Edit the stock ticker lists in the config files:

- **BSE stocks:** `src/config/stocks.json`
- **NSE stocks:** `src/config/nse_stocks.json`

Format:
```json
{
  "stocks": ["TCS.BO", "RELIANCE.BO", "INFY.BO"]
}
```

> Use `.BO` suffix for BSE and `.NS` suffix for NSE tickers (Yahoo Finance format).

### Automated Daily Analysis

Use the provided shell script to run both BSE and NSE analysis:

```bash
chmod +x run_daily.sh
./run_daily.sh
```

You can schedule this with `cron` for automated daily updates:

```bash
# Example: Run every day at 6 PM IST
0 18 * * * /path/to/StockMarketVolatility/run_daily.sh >> /path/to/logs/analysis.log 2>&1
```

---

## 🔧 Real-time Features (Optional)

For live intraday price streaming, you need **Redis** running locally:

```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Or run directly
redis-server
```

The web app will automatically connect to Redis on `localhost:6379` and listen for real-time price and volatility updates via WebSockets.

---

## 📊 Signal Logic

The trading signal engine uses this logic:

| Signal | Condition |
|---|---|
| **BUY** | Forecast volatility < Current volatility × 0.95 |
| **SELL** | Forecast volatility > Current volatility × 1.05 |
| **STRONG SELL** | SELL condition + High gamma (leverage effect > 0.1) |
| **CAUTION** | HOLD condition + High gamma |
| **HOLD** | Volatility is stable |

---

## 🧪 Backtest Strategy

The backtester simulates a volatility-based trading strategy:

- **BUY** when volatility drops > 5% (market stabilizing)
- **SELL** when volatility rises > 5% (risk increasing)
- Compares strategy equity curve against a **Buy & Hold** benchmark
- Starting capital: ₹10,000

---

## 📦 Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO, Eventlet
- **Data:** yfinance, pandas, NumPy
- **Models:** statsmodels (ARMA), arch (GARCH/TGARCH)
- **Frontend:** Jinja2, HTML/CSS/JS, Chart.js
- **Real-time:** Redis pub/sub, WebSockets
- **PDF Export:** WeasyPrint
- **Scheduling:** Flask-APScheduler

---

## 📝 License

This project is for educational and research purposes.