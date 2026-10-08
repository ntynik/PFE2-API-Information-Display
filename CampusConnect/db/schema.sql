-- SQLite schema
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    preferences TEXT
);

DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    location TEXT,
    date TEXT
);

-- Create external scraped events table here
DROP TABLE IF EXISTS external_events;
CREATE TABLE external_events (
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
);

DROP TABLE IF EXISTS api_data;
CREATE TABLE api_data (
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
);