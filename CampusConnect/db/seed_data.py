import sqlite3
import os

DB_PATH = "db/campusconnect.db"

# Remove existing DB for a clean seed (optional in dev environment)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables manually or run schema.sql separately if preferred
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    preferences TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    location TEXT,
    date TEXT
)''')

# Creates external events table
c.execute('''CREATE TABLE IF NOT EXISTS external_events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    start_date TEXT,
    start_time TEXT,
    end_date TEXT,
    end_time TEXT,
    location TEXT,
    address TEXT,
    url TEXT,
    description TEXT
)''')

# Creates api data table
c.execute('''CREATE TABLE IF NOT EXISTS api_data (
    id INTEGER PRIMARY KEY,
    ticketmaster_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    start_date TEXT,
    start_time TEXT,
    end_date TEXT,
    end_time TEXT,
    location TEXT,
    address TEXT,
    url TEXT,
    description TEXT
)''')

# Create Users Seed Data
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Alice", "Aly"))
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Bob", "art, Bobby"))
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Charlie", "Chaz"))

# Internal Events Seed Data
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Music Night", "Student Center", "2025-04-05"))
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Hackathon", "Library", "2025-04-01"))
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Art Exhibition", "Gallery", "2025-04-10"))
c.execute("SELECT title, location, date FROM events")

# External Events Seed Data
c.execute("INSERT INTO external_events (title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Music Festival", "April 20", "9:00am", "April 21", "11:00pm", "Student Center", "100 Belmont-Mt Holly Rd, Belmont, NC 28012", "https://test.com", "Music Festival"))
c.execute("INSERT INTO external_events (title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Game Night", "April 21", "9:00pm", None, "11:00pm", "Student Center", "100 Belmont-Mt Holly Rd, Belmont, NC 28012", "https://test.com", "Game Night"))
c.execute("INSERT INTO external_events (title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Earth Day", "April 22", None, None, None, None, None, "https://test.com", "Earth Day"))

# API Data Seed Data
c.execute("INSERT INTO api_data (ticketmaster_id, title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("ABCDEF123", "Music Festival", "April 20", "9:00am", "April 21", "11:00pm", "Student Center", "100 Belmont-Mt Holly Rd, Belmont, NC 28012", "https://test.com", "Music Festival"))
c.execute("INSERT INTO api_data (ticketmaster_id, title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("ABCDEF456", "Game Night", "April 21", "9:00pm", None, "11:00pm", "Student Center", "100 Belmont-Mt Holly Rd, Belmont, NC 28012", "https://test.com", "Game Night"))
c.execute("INSERT INTO api_data (ticketmaster_id, title, start_date, start_time, end_date, end_time, location, address, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("ABCDEF789", "Earth Day", "April 22", None, None, None, None, None, "https://test.com", "Earth Day"))

conn.commit()
conn.close()