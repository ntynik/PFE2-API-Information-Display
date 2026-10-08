import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os

class CampusEventScraper:
    """
    A class to extract data from the Adrian College events calendar and render it to an endpoint.

    Attributes:
    -----------
    url : str
        The url of the Adrian College events calendar
        
    headers : str
        The headers to send with the request

    Methods:
    --------
    scrape_events():
        Retrieves event information from the Adrian College events calendar, 
        stores the information for each event in a dictionary, 
        and returns a list containing all event dictionaries

    add_to_table():
        Takes a dictionary containing event information as input 
        and inserts the data into the campusconnect.db external_events table
    """
    # Initializes class object with url and headers parameters
    def __init__(self, url, headers):
        """
        Constructs the necessary attributes for the APIClient object

        Parameters:
        -----------
        url : str
            The url of the Adrian College events calendar

        headers : str
            The headers to send with the request
        """
        self.url = url
        self.headers = headers

    # Scrapes events from the Adrian College calendar
    def scrape_events(self):
        """
        Retrieves event information from the Adrian College events calendar, 
        stores the information for each event in a dictionary, 
        and returns a list containing all event dictionaries
        
        Returns:
        --------
        list_dicts : lst
            A list containing all event dictionaries
        """
        # Sends the get request
        get_data = requests.get(self.url, headers=self.headers)

        # Retreive the webpage's content from the GET request
        webpage = BeautifulSoup(get_data.content, 'html.parser')

        # Retrieve a list of only the events from the webpage's content
        event_list = webpage.find_all('a', class_= "event")

        # Creates an empty list to store dictionaries containing the event information
        list_dicts = []

        # Retrieves the necessary information from each event
        for event in event_list:
            # Retreives the event page url and formats it into a usable url
            url = event.get('href')
            url = "https://adrian.edu" + url

            # Retreives the event title and formats it
            title = event.find('p', class_='title')
            title = title.get_text().strip()

            # Retreives information from the webpage for the individual event, not the event calendar
            get_data = requests.get(url, headers=self.headers)
            webpage = BeautifulSoup(get_data.content, 'html.parser')

            # Adds a delay to avoid requests getting blocked
            time.sleep(1.2)

            # Retreives the time and date the event is occurring
            time_and_date = webpage.find('p', class_='dates')
            time_and_date = time_and_date.get_text().strip()
            time_and_date = time_and_date.replace(",", "")

            # Splits the time and date information so individual elements can be extracted
            time_date_list = time_and_date.split()
            list_length = len(time_date_list)

            # Creates variables to store the individual elements that will later be stored in the database
            start_date = None
            end_date = None
            start_time = None
            end_time = None
            location = None
            address = None

            # Retreives date and time information from the event
            if list_length == 3:
                start_date = time_date_list[0] + " " + time_date_list[1]
            elif list_length == 6:
                start_date = time_date_list[0] + " " + time_date_list[1]
                start_time = time_date_list[3]
                end_time = time_date_list[5]
            elif list_length == 7:
                start_date = time_date_list[0] + " " + time_date_list[1]
                start_time = time_date_list[2]
                end_date = time_date_list[4] + " " + time_date_list[5]
                end_time = time_date_list[6]

            # Retrieves the event's description
            description = webpage.find('div', id='content-7030')
            description = description.get_text().strip()

            # Splits the description so information on the address and location can be stored seperately
            description_split = description.split("\n")
            
            # Replaces any empty strings with a None value for consistency with other elements
            if description == "":
                description = None
            
            # Seperate logic for descriptions that contain a location and address
            if len(description_split) >= 3:
                location = description_split[0]
                address = description_split[1]

                # Puts the description back together without the location and address lines
                description_split = description_split[2:]
                description_new = ""
                for item in description_split:
                    description_new += item
                    description_new += "\n"
                description = description_new
                description.strip()

            # Create a dictionary with the event information
            event_dict = {
            "title" : title,
            "start_date" : start_date,
            "start_time" : start_time,
            "end_date" : end_date,
            "end_time" : end_time,
            "location" : location,
            "address" : address,
            "url" : url,
            "description" : description
            }

            # Store every event's dictionary in a list
            list_dicts.append(event_dict)

        # Return the list of event dictionaries
        return list_dicts
    
    # Adds data to the external_events table
    def add_to_table(self, scraped_data):
        """
        Takes a dictionary containing event information as input 
        and inserts the data into the campusconnect.db external_events table

        Parameters:
        -----------
        scraped_date : lst
            A list of dictionaries that contain information on events retrieved from the Adrian College events calendar
        """
        # Finds path to the database file
        DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campusconnect.db')
        DB_PATH = os.path.abspath(DB_PATH)

        # Establishes a connection to campusonnect.db
        connection = sqlite3.connect(DB_PATH)

        # Create a cursor to execute SQL commands on campuconnect.db
        cursor = connection.cursor()

        # If the external_events table already exists, delete it
        cursor.execute('''DROP TABLE IF EXISTS external_events;''')

        # Creates the external_events table
        cursor.execute("CREATE TABLE external_events (id INTEGER PRIMARY KEY, title TEXT NOT NULL, start_date TEXT, start_time TEXT, end_date TEXT, end_time TEXT, location TEXT, address TEXT, url TEXT, description TEXT)")

        # Insert scraped data into the external_events table
        for i in range(len(scraped_data)):
            title = scraped_data[i]["title"]
            start_date = scraped_data[i]["start_date"]
            start_time = scraped_data[i]["start_time"]
            end_date = scraped_data[i]["end_date"]
            end_time = scraped_data[i]["end_time"]
            location = scraped_data[i]["location"]
            address = scraped_data[i]["address"]
            url = scraped_data[i]["url"]
            description = scraped_data[i]["description"]

            to_execute = '''INSERT INTO external_events (title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            cursor.execute(to_execute, (title, start_date, start_time, end_date, end_time, location, address, url, description))

        # Save any changes made to the database file
        connection.commit()

        # Close the connection so no unintended changes can be made
        connection.close()