"""Database functions for managing posts."""
import sqlite3
import json
from datetime import datetime


def create_post(post):
    """Inserts a new post into the database."""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        Insert into Posts (user_id, category_id, title, publication_date, image_url, content, approved) values (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                post["user_id"],
                post["category_id"],
                post["title"],
                datetime.now(),
                post.get("image_url", ""),
                post["content"],
                1,
            ),
        )

        id = db_cursor.lastrowid

        return json.dumps({"id": id})


def get_all_posts():
    """Returns all posts from the database."""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
                    SELECT
                        p.id,
                        p.title,
                        p.publication_date,
                        p.image_url,
                        p.content,
                        p.approved,
                        u.id,
                        u.first_name || ' ' || u.last_name AS author,
                        c.label AS category
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.id
                    JOIN Categories c ON p.category_id = c.id
                """
        )

        query_results = db_cursor.fetchall()

        posts = []

        for row in query_results:
            posts.append(dict(row))

        return json.dumps(posts)


def get_single_users_post(user_id):
    """Returns all posts belonging to a specific user."""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """ 
                    SELECT
                        p.id AS post_id,
                        p.title,
                        p.publication_date,
                        p.image_url,
                        p.content,
                        p.approved,
                        u.id AS user_id,
                        u.first_name || ' ' || u.last_name AS author,
                        c.label AS category
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.id
                    JOIN Categories c ON p.category_id = c.id
                    WHERE p.user_id = ?
                """,
            (user_id,),
        )

        dataset = db_cursor.fetchall()
        posts = [dict(row) for row in dataset]

        return json.dumps(posts)


def get_post_details(post_id):
    """Returns the details of a single post by its id."""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
                    SELECT
                        p.id AS post_id,
                        p.title,
                        p.publication_date,
                        p.image_url,
                        p.content,
                        p.approved,
                        u.first_name || ' ' || u.last_name AS author,
                        c.label AS category
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.id
                    JOIN Categories c ON p.category_id = c.id
                    WHERE p.id = ?
                """,
            (post_id,),
        )

        row = db_cursor.fetchone()

        if row:
            return json.dumps(dict(row))
        else:
            return json.dumps({})