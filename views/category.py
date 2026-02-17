import sqlite3
import json
from datetime import datetime

def get_all_categories():
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute("""
            SELECT
                *
            FROM Categories c               
        """)

        query_results = db_cursor.fetchall()

        categories = []

        for row in query_results:
            categories.append(dict(row))

        return json.dumps(categories)