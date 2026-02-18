#!/bin/bash

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run analysis
echo "Running Stock Analysis for $(date)..."
python src/run_stock_analysis.py
python src/run_nse_analysis.py

echo "Analysis complete. Dashboard updated."
