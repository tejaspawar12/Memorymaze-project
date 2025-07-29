# app/database.py

import sqlite3
import os

DB_NAME = "users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
