from flask import Flask, Response, jsonify, g, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import os
from sources.data_fetcher import get_dates_to_update, update_data_for_date, cleanup_old_files, load_data_from_file, get_all_dates_range
from sources.ical_generator import generate_ical_for_league

app = Flask(__name__)

# Logging setup
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# General logging with rotation
log_file = os.path.join(log_dir, 'app.log')
handler = TimedRotatingFileHandler(log_file, when='D', backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Access logging (separate)
access_log_file = os.path.join(log_dir, 'access.log')
access_handler = TimedRotatingFileHandler(access_log_file, when='D', backupCount=7)
access_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger = logging.getLogger('access')
logger.setLevel(logging.INFO)
logger.addHandler(access_handler)

last_call_time = 0

@app.before_request
def log_request_info():
    g.start_time = time.time()

@app.after_request
def log_response_info(response):
    # Log: time + endpoint + response status + response time
    response_time = time.time() - g.start_time
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {request.path} - {response.status_code} - {response_time:.2f}s")
    return response

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/build')
def build():
    return jsonify({"version": "1.0.0"})

@app.route('/leagues')
def leagues():
    today = get_dates_to_update()[0]
    data = load_data_from_file(today)
    if not data:
        return jsonify([])

    leagues_list = []
    for league in data.get('leagues', []):
        leagues_list.append({
            "name": league.get('name'),
            "url_name": league.get('url_name')
        })
    return jsonify(leagues_list)

@app.route('/league/<league_url_name>.ics')
def league_ical(league_url_name):
    # Load data from last 3 months to next 30 days
    dates = get_all_dates_range()
    all_leagues = {}
    for date in dates:
        data = load_data_from_file(date)
        if data:
            for league in data.get('leagues', []):
                url_name = league.get('url_name')
                if url_name not in all_leagues:
                    all_leagues[url_name] = league.copy()
                    all_leagues[url_name]['games'] = []
                all_leagues[url_name]['games'].extend(league.get('games', []))

    if league_url_name not in all_leagues:
        return Response("League not found", status=404)

    ical_data = generate_ical_for_league(all_leagues[league_url_name])
    return Response(ical_data, mimetype='text/calendar')

def update_task():
    global last_call_time
    dates = get_dates_to_update()
    for date in dates:
        if update_data_for_date(date, last_call_time):
            last_call_time = time.time()
    cleanup_old_files()

if __name__ == '__main__':
    # Initial update
    update_task()

    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_task, IntervalTrigger(minutes=30))
    scheduler.start()

    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=False)