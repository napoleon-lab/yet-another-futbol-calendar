import requests
import os
import json
import time
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

DATA_DIR = 'data/futbol'

def fetch_data_for_date(date):
    """Fetch data from API for a given date (DD-MM-YYYY)"""
    url = f'https://api.promiedos.com.ar/games/{date}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_data_to_file(data, date):
    """Save data to JSON file"""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, f'{date}-promiedos.json')
    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_data_from_file(date):
    """Load data from JSON file if exists"""
    file_path = os.path.join(DATA_DIR, f'{date}-promiedos.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def get_update_threshold(date_str):
    """Get the update threshold in seconds based on how close the date is"""
    date = datetime.strptime(date_str, '%d-%m-%Y')
    now = datetime.now()
    days_diff = (date - now).days

    if days_diff <= 2:
        # Close events: update every 6 hours
        return 6 * 3600
    elif days_diff > 7:
        # Far events: update every 24 hours
        return 24 * 3600
    else:
        # Medium: update every 12 hours
        return 12 * 3600

def needs_update(date_str):
    """Check if data for date needs update based on file mtime"""
    file_path = os.path.join(DATA_DIR, f'{date_str}-promiedos.json')
    if not os.path.exists(file_path):
        return True

    mtime = os.path.getmtime(file_path)
    threshold = get_update_threshold(date_str)
    return time.time() - mtime > threshold

def update_data_for_date(date_str, last_call_time):
    """Update data for date if needed, respecting rate limit"""
    if not needs_update(date_str):
        return False

    # Rate limiting: at least 1 + random(0,30) minutes since last call
    min_interval = 60 + random.randint(0, 30 * 60)  # 1 min + 0-30 min
    if time.time() - last_call_time < min_interval:
        return False

    try:
        logger.info(f"Updating data for {date_str}")
        data = fetch_data_for_date(date_str)
        save_data_to_file(data, date_str)
        logger.info(f"Successfully updated data for {date_str}")
        return True
    except Exception as e:
        logger.error(f"Error updating data for {date_str}: {e}")
        return False

def cleanup_old_files():
    """Delete files older than 3 months"""
    cutoff = time.time() - 3 * 30 * 24 * 3600  # approx 3 months
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('-promiedos.json'):
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.getmtime(file_path) < cutoff:
                os.remove(file_path)
                logger.info(f"Deleted old file: {filename}")

def get_dates_to_update():
    """Get list of dates for next 30 days"""
    dates = []
    today = datetime.now()
    for i in range(30):
        date = today + timedelta(days=i)
        dates.append(date.strftime('%d-%m-%Y'))
    return dates