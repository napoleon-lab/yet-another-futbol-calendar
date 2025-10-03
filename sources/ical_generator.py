from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

def parse_start_time(start_time_str):
    """Parse start_time string to datetime with timezone"""
    # Format: "DD-MM-YYYY HH:MM"
    dt = datetime.strptime(start_time_str, '%d-%m-%Y %H:%M')
    # Assume local timezone America/Buenos_Aires (UTC-3)
    local_tz = pytz.timezone('America/Buenos_Aires')
    dt = local_tz.localize(dt)
    return dt

def generate_ical_for_league(league_data):
    """Generate iCalendar for a league"""
    cal = Calendar()
    cal.add('prodid', '-//Sports Calendar//sports-webcalendar//')
    cal.add('version', '2.0')
    cal.add('name', league_data.get('name', 'Unknown League'))
    cal.add('X-WR-CALNAME', league_data.get('name', 'Unknown League'))

    for game in league_data.get('games', []):
        event = Event()
        teams = game.get('teams', [])
        if len(teams) == 2:
            team1 = teams[0].get('name', 'Team 1')
            team2 = teams[1].get('name', 'Team 2')
            summary = f"{team1} vs {team2}"
        else:
            summary = "Unknown Match"

        start_time_str = game.get('start_time', '')
        try:
            start_dt = parse_start_time(start_time_str)
            event.add('dtstart', start_dt)
            # Assume duration 2 hours
            event.add('dtend', start_dt + timedelta(hours=2))
        except ValueError:
            continue  # Skip if invalid time

        event.add('summary', summary)

        tv_networks = game.get('tv_networks', [])
        tv_names = [tv.get('name', '') for tv in tv_networks]
        description = f"TV: {', '.join(tv_names)}" if tv_names else "No TV info"
        event.add('description', description)

        event.add('location', league_data.get('name', ''))

        cal.add_component(event)

    return cal.to_ical().decode('utf-8')