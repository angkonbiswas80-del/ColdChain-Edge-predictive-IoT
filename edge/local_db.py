import sqlite3
import json
from datetime import datetime

DB_NAME = "coldchain_edge.db"

def init_local_database():
    """
    Initializes the local SQLite database and creates the buffered_telemetry table 
    if it does not already exist.
    """
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    # Create table to buffer data when offline
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buffered_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            shock REAL NOT NULL,
            status TEXT NOT NULL,
            synced INTEGER DEFAULT 0
        )
    """)
    
    connection.commit()
    connection.close()
    print("💾 Local SQLite Buffer Database Initialized Successfully.")

def buffer_telemetry_data(data):
    """
    Saves a telemetry payload to the local database when the system is offline.
    """
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT INTO buffered_telemetry (timestamp, temperature, humidity, shock, status, synced)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (data['timestamp'], data['temperature'], data['humidity'], data['shock'], data['status']))
    
    connection.commit()
    connection.close()
    print(f"⚠️ Network offline. Packet buffered locally at {data['timestamp']}")

def get_unsynced_data():
    """
    Fetches all telemetry packets that haven't been synchronized with the cloud yet.
    """
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, timestamp, temperature, humidity, shock, status FROM buffered_telemetry WHERE synced = 0")
    rows = cursor.fetchall()
    connection.close()
    
    # Convert database rows to a clean list of dictionaries
    unsynced_packets = []
    for row in rows:
        unsynced_packets.append({
            "id": row[0],
            "timestamp": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "shock": row[4],
            "status": row[5]
        })
    return unsynced_packets

def mark_as_synced(packet_id):
    """
    Marks a specific packet as synchronized or deletes it to free up edge storage.
    """
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    # Deleting instead of just updating flag prevents SQLite from growing indefinitely on an Edge Node
    cursor.execute("DELETE FROM buffered_telemetry WHERE id = ?", (packet_id,))
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    # Test database initialization
    init_local_database()