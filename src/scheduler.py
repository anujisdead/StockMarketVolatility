from flask_apscheduler import APScheduler
import logging
import sys
import os

# Ensure we can import modules in the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_stock_analysis import main as run_bse_analysis
from run_nse_analysis import main as run_nse_analysis

class SchedulerConfig:
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

def update_market_data():
    """
    Scheduled job to run volatility analysis for both markets.
    """
    logging.info("--- Scheduled Job Started: Market Data Update ---")
    try:
        logging.info("Running BSE Analysis...")
        run_bse_analysis()
        logging.info("BSE Analysis Complete.")
        
        logging.info("Running NSE Analysis...")
        run_nse_analysis()
        logging.info("NSE Analysis Complete.")
        
        logging.info("--- Scheduled Job Completed Successfully ---")
    except Exception as e:
        logging.error(f"Error during scheduled market update: {e}")

def init_scheduler(app):
    """
    Initialize the scheduler and add the recurring job.
    """
    app.config.from_object(SchedulerConfig())
    
    # Run every 15 minutes
    # trigger='interval' means it runs periodically
    scheduler.add_job(id='update_market_data', func=update_market_data, trigger='interval', minutes=15)
    
    scheduler.init_app(app)
    scheduler.start()
    logging.info("Scheduler started. Job 'update_market_data' registered for 15-minute interval.")
