import os
from flask import Blueprint, render_template
import sqlite3
from utils import event_scraper
event_bp = Blueprint('event', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campusconnect.db')
DB_PATH = os.path.abspath(DB_PATH)  # Ensures full absolute path

@event_bp.route("/events")
def events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Fetch internal events - Example
    cursor.execute("SELECT title, location, date FROM events")
    internal_events = cursor.fetchall()
    # Print out values for debugging
    print(internal_events)

    # Fetch external events 
    # Update the extenal_events variable with the data you want to display
    external_events = []

    # Create a CampusEventScraper object and pass in the url and headers
    college_scraper = event_scraper.CampusEventScraper("https://www.adrian.edu/calendar", {'User-Agent': 'Mozilla/5.0 (compatible; ProgrammingForEveryoneIIAssignmentBot/1.0; +nathantynik@abbey.bac.edu)'})
    
    # Run the functions needed to retrieve the data from the college event calendar and store it in the external_events table
    scraped_events = college_scraper.scrape_events()
    college_scraper.add_to_table(scraped_events)

    # Retrieve all the event information stored in the external_events table and store it in the empty list
    cursor.execute('SELECT * from external_events;')
    rows = cursor.fetchall()
    for row in rows: 
        external_events.append({
            "id": row[0],
            "title": row[1],
            "start_date": row[2],
            "start_time": row[3],
            "end_date": row[4],
            "end_time": row[5],
            "location": row[6],
            "address": row[7],
            "url": row[8],
            "description": row[9]
        })

    # Close the connection to prevent any accidental changes
    conn.close()

    # Pass the list containing the event information to the render template
    return render_template("events.html", internal_events=internal_events, external_events=external_events)