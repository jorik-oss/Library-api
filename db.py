import sqlite3

def get_db_connection():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn