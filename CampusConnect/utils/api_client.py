import requests
from datetime import datetime, timezone
import sqlite3
import os

class APIClient:
    """
    A class to extract data from the TicketMaster Discovery API and render it to an endpoint.

    Attributes:
    -----------
    url : str
        The url of the TicketMaster Discovery API

    headers : str
        The headers to send with the request

    api_key : str
        The TicketMaster Discovery API key

    Methods:
    --------
    convert_time():
        Converts a time in the 24 hour format to the corresponding time in the 12 hour format
        
    convert_date():
        Converts a date from ISO format to month day format

    scrape_api():
        Retrieves event information from the TicketMaster API, 
        stores the information for each event in a dictionary, 
        and returns a list containing all event dictionaries

    add_to_table():
        Takes a dictionary containing event information as input 
        and inserts the data into the campusconnect.db api_data table
    """
    # Initializes class object with url, headers and api_key parameters
    def __init__(self, url, headers):
        """
        Constructs the necessary attributes for the APIClient object

        Parameters:
        -----------
        url : str
            The url of the TicketMaster Discovery API

        headers : str
            The headers to send with the request

        api_key : str
            The TicketMaster Discovery API key
        """
        self.url = url
        self.headers = headers
        self.api_key = "TICKETMASTER_API"

    # Converts time from 24 hour format to 12 hour format
    def convert_time(self, time):
        """
        Converts a time in the 24 hour format to the corresponding time in the 12 hour format

        Parameters:
        -----------
        time : str
            A string containing the time in the 24 hour format

        Returns:
        --------
         : str
            A string containing the time in 12 hour format
        """
        time_split = time.split(":")
        time_int = int(time_split[0])

        if time_int >= 13 and time_int < 24:
            time_new = time_int - 12
            return str(time_new) + ":" + time_split[1] + "pm"
        elif time_int >= 12 and time_int < 13:
            return "12:" + time_split[1] + "pm"
        elif time_int >= 1 and time_int < 12:
            return time_split[0] + ":" + time_split[1] + "am"
        else:
            return "12:" + time_split[1] + "am"

    # Convert from ISO date format to regular month day format
    def convert_date(self, date):
        """
        Converts a date from ISO format to month day format

        Parameters:
        -----------
        date : str
            A string containing the date in ISO format
        
        Returns:
        --------
         : str
            A string containing the date in month day format
        """
        date_split = date.split("-")
        date_map = {
            "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June", 
            "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"
        }

        return date_map[date_split[1]] + " " + date_split[2]

    # Scrapes events from the Ticketmaster Discovery API
    def scrape_api(self):
        """
        Retrieves event information from the TicketMaster API, 
        stores the information for each event in a dictionary, 
        and returns a list containing all event dictionaries
        
        Returns:
        --------
        list_dicts : lst
            A list containing all event dictionaries
        """
        # Gets the current time and date and converts it to a recognizable format for the API
        start_date_time = datetime.now(timezone.utc).isoformat()
        split_time = start_date_time.split(".")
        start_date_time = split_time[0] + "Z"

        # Set up the parameters for the get request
        params = {
            "apikey": self.api_key,
            "city": "Charlotte",
            "stateCode": "NC",
            "countryCode": "US",
            "startDateTime": start_date_time,
            "size": 35,
            "page": 0,
            "sort": "date,asc"
            }

        # Sends the get request
        get_data = requests.get(self.url, headers=self.headers, params=params)

        # Retrieves the json response from the get request
        data = get_data.json()

        # Retrieves the events from the json response
        events = data.get("_embedded", {}).get("events", [])

        # Creates an empty list to store dictionaries containing event data
        list_dicts = []

        # Retrieves the necessary information from each event
        for event in events:
            # Retrieves the name of the event
            ticketmaster_id = event.get("id", "")
            title = event.get("name", "")

            # Retrieves the start and end dates for the event and converts them into normal month day format
            date = event.get("dates", {})

            start_date = date.get("start", {}).get("localDate", "")
            start_date = self.convert_date(start_date)

            end_date = date.get("end", {}).get("localDate", "")
            if end_date:
                end_date = self.convert_date(end_date)

            # Retrieves the start and end times for the event and converts them into 12 hour format
            start_time = date.get("start", {}).get("localTime", "")
            start_time = self.convert_time(start_time)
            
            end_time = date.get("end", {}).get("localTime", "")
            if end_time:
                end_time = self.convert_time(end_time)

            # Retrieves the name of the venue where the event is taking place and the address of the venue
            embedded = event.get("_embedded", {})
            venues = embedded.get("venues", [])
            if venues:
                venue = venues[0]
            else:
                venue = {}

            location = venue.get("name", "")
            address = venue.get("address", {}).get("line1", "")

            # Retrieves the url for the individual event page
            url = event.get("url", "")

            # Retrieves a description of the event
            description = event.get("info", "")

            # Creates a dictionary containing the information on the event
            event_dict = {
                "ticketmaster_id": ticketmaster_id,
                "title": title,
                "start_date": start_date,
                "start_time": start_time,
                "end_date": end_date,
                "end_time": end_time,
                "location": location,
                "address": address,
                "url": url,
                "description": description
            }

            # Stores the dictionary containing the event information in the list of dictionaries
            list_dicts.append(event_dict)

        # Returns the list of event dictionaries
        return list_dicts

    # Adds data to the api_data table
    def add_to_table(self, scraped_data):
        """
        Takes a dictionary containing event information as input 
        and inserts the data into the campusconnect.db api_data table

        Parameters:
        -----------
        scraped_date : lst
            A list of dictionaries that contain information on events retrieved from the API
        """
        # Finds path to the database file
        DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campusconnect.db')
        DB_PATH = os.path.abspath(DB_PATH)

        # Establishes a connection to campusonnect.db
        connection = sqlite3.connect(DB_PATH)

        # Create a cursor to execute SQL commands on campuconnect.db
        cursor = connection.cursor()

        # If the api_data table already exists, delete it
        cursor.execute('''DROP TABLE IF EXISTS api_data;''')

        # Creates the api_data table
        cursor.execute("CREATE TABLE api_data (id INTEGER PRIMARY KEY, ticketmaster_id TEXT NOT NULL UNIQUE, title TEXT NOT NULL, start_date TEXT, start_time TEXT, end_date TEXT, end_time TEXT, location TEXT, address TEXT, url TEXT, description TEXT)")

        # Insert scraped data into the api_data table
        for i in range(len(scraped_data)):
            ticketmaster_id = scraped_data[i]["ticketmaster_id"]
            title = scraped_data[i]["title"]
            start_date = scraped_data[i]["start_date"]
            start_time = scraped_data[i]["start_time"]
            end_date = scraped_data[i]["end_date"]
            end_time = scraped_data[i]["end_time"]
            location = scraped_data[i]["location"]
            address = scraped_data[i]["address"]
            url = scraped_data[i]["url"]
            description = scraped_data[i]["description"]

            to_execute = '''INSERT INTO api_data (title, ticketmaster_id, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            cursor.execute(to_execute, (title, ticketmaster_id, start_date, start_time, end_date, end_time, location, address, url, description))

        # Save any changes made to the database file
        connection.commit()

        # Close the connection so no unintended changes can be made
        connection.close()
