import sqlite3
import json
from datetime import datetime

def create_subscription(subscription):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Subscriptions
            ( follower_id, author_id, created_on )
        VALUES
            ( ?, ?, ? );
        """, (
            subscription['follower_id'], 
            subscription['author_id'], 
            subscription.get('created_on', datetime.now().strftime("%Y-%m-%d"))
        ))

        id = db_cursor.lastrowid
        subscription['id'] = id

    return json.dumps(subscription)

def get_all_subscriptions(query_params):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            s.id,
            s.follower_id,
            s.author_id,
            s.created_on,
            s.end_datetime
        FROM Subscriptions s
        """)

        subscriptions = []
        dataset = db_cursor.fetchall()

        for row in dataset:
            subscriptions.append(dict(row))

    return json.dumps(subscriptions)

def end_subscription(pk):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
            UPDATE Subscriptions
            SET end_datetime = DATETIME('now')
            WHERE id = ?
        """, (pk,))

        return db_cursor.rowcount > 0

def delete_subscription(pk):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
            DELETE FROM Subscriptions
            WHERE id = ?
        """, (pk,))

        conn.commit()
        return db_cursor.rowcount > 0