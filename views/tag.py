import sqlite3
import json


def create_tag(tag):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        INSERT INTO Tags (label) VALUES (?)
        """,
            (tag["label"],),
        )

        # Get the ID of the row we just created
        id = db_cursor.lastrowid

        # Return the new object so React knows it was successful
        return json.dumps({"id": id, "label": tag["label"]})


def get_all_tags():
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                t.id,
                t.label
            FROM Tags t 
            ORDER BY t.label ASC              
        """
        )

        query_results = db_cursor.fetchall()

        tags = []

        for row in query_results:
            tags.append(dict(row))

        return json.dumps(tags)


def delete_tag(pk):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to delete the chosen order
        db_cursor.execute(
            """ 
        DELETE FROM Tags WHERE id = ?
        """,
            (pk,),
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False
