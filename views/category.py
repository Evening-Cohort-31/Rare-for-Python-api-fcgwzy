import sqlite3
import json


def create_category(category):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        INSERT INTO Categories (label) VALUES (?)
        """,
            (category["label"],),
        )  # Fixed the binding with a comma

        # Get the ID of the row we just created
        id = db_cursor.lastrowid

        # Return the new object so React knows it was successful
        return json.dumps({"id": id, "label": category["label"]})


def get_all_categories():
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute(
            """
            SELECT
                c.id,
                c.label
            FROM Categories c               
        """
        )

        query_results = db_cursor.fetchall()

        categories = []

        for row in query_results:
            categories.append(dict(row))

        return json.dumps(categories)


def delete_category(pk):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to delete the chosen order
        db_cursor.execute(""" 
        DELETE FROM Categories WHERE id = ?
        """, (pk,))
        number_of_rows_deleted = db_cursor.rowcount
    
    return True if number_of_rows_deleted > 0 else False
