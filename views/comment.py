import sqlite3
import json
from datetime import datetime


def create_comment(comment):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        db_cursor.execute(
            """
        Insert into Comments (post_id, author_id, publication_date, subject, content) values (?, ?, ?, ?)
        """,
            (
                comment["post_id"],
                comment["author_id"],
                current_date,
                comment["subject"],
                comment["content"],
            ),
        )

        id = db_cursor.lastrowid

        return json.dumps(
            {
                "id": id,
                "post_id": comment["post_id"],
                "author_id": comment["author_id"],
                "publication_date": current_date,
                "subject": comment["subject"],
                "content": comment["content"],
            }
        )


def get_all_comments_for_post(post_id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute(
            """
            SELECT 
                c.id,
                c.post_id,
                c.author_id,
                c.publication_date,
                c.subject,
                c.content,
                u.username
            FROM Comments c
            JOIN Posts p ON c.post_id = p.id
            JOIN Users u ON c.author_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.publication_date DESC
        """, (post_id, )
        )

        query_results = db_cursor.fetchall()

        comments = []

        for row in query_results:
            comments.append(dict(row))

        return json.dumps(comments)
    
    
def get_all_users_comments():
        with sqlite3.connect("./db.sqlite3") as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # We join the tables so we get names/prices instead of just ID numbers
            db_cursor.execute(
                """
                SELECT 
                    c.id,
                    c.post_id,
                    c.author_id,
                    c.publication_date,
                    c.subject,
                    c.content,
                    u.username
                FROM Comments c
                JOIN Posts p ON c.post_id = p.id
                JOIN Users u ON c.author_id = u.id
            """
            )

            query_results = db_cursor.fetchall()

            comments = [dict(row) for row in query_results]

            return json.dumps(comments)
    