from flask import Blueprint, render_template
import os
import sqlite3
from utils import api_client
api_bp = Blueprint('api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campusconnect.db')
DB_PATH = os.path.abspath(DB_PATH)  # Ensures full absolute path

@api_bp.route("/api")
def api():
    # Open connection to campusconnect.db
    conn = sqlite3.connect(DB_PATH)
    
    # Create cursor to modify the database
    cursor = conn.cursor()

    # Create an emtpy list to hold the api data
    api_data = []
    
    # Create an APIClient object and pass in the url and headers
    api_scraper = api_client.APIClient("https://app.ticketmaster.com/discovery/v2/events.json", {'User-Agent': 'Mozilla/5.0 (compatible; ProgrammingForEveryoneIIAssignmentBot/1.0; +nathantynik@abbey.bac.edu)'})
    
    # Run the functions needed to retrieve the data from the API and store it in the api_data table
    scraped_events = api_scraper.scrape_api()
    api_scraper.add_to_table(scraped_events)

    # Retrieve all the event information stored in the api_data table and store it in the empty list
    cursor.execute('SELECT * from api_data;')
    rows = cursor.fetchall()
    for row in rows: 
        api_data.append({
            "id": row[0],
            "ticketmaster_id": row[1],
            "title": row[2],
            "start_date": row[3],
            "start_time": row[4],
            "end_date": row[5],
            "end_time": row[6],
            "location": row[7],
            "address": row[8],
            "url": row[9],
            "description": row[10]
        })

    # Close the connection to prevent any accidental changes
    conn.close()

    # Pass the list containing the event information to the render template
    return render_template("api.html", api_data=api_data)
