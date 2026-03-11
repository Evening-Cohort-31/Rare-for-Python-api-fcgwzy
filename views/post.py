"""Database functions for managing posts."""

import sqlite3
import json
from datetime import datetime
from .user import user_is_admin


def create_post(post, user_id):
    """Inserts a new post into the database."""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        approved = 1 if user_is_admin(user_id) else 0

        db_cursor.execute(
            """
        Insert into Posts (user_id, category_id, title, publication_date, image_url, content, approved) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                post["category_id"],
                post["title"],
                datetime.now(),
                post.get("image_url", ""),
                post["content"],
                approved,
            ),
        )

        new_post_id = db_cursor.lastrowid

        return json.dumps({"id": new_post_id})


def get_all_posts():
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
                p.user_id,
                u.first_name || ' ' || u.last_name AS author,
                c.label AS category
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            JOIN Categories c ON p.category_id = c.id
            WHERE p.approved = 1
            AND p.publication_date <= DATETIME('now')
            ORDER BY p.publication_date DESC;
            """
        )

        # ONLY CALL THIS ONCE
        dataset = db_cursor.fetchall()

        posts = []
        for row in dataset:
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
                        p.user_id,
                        u.first_name || ' ' || u.last_name AS author,
                        c.id AS category_id
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
                p.user_id,
                u.first_name || ' ' || u.last_name AS author,
                c.id AS category_id,
                t.id AS tag_id,
                t.label AS tag_label
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            JOIN Categories c ON p.category_id = c.id
            LEFT JOIN PostTags pt ON pt.post_id = p.id
            LEFT JOIN Tags t ON t.id = pt.tag_id
            WHERE p.id = ?
        """,
            (post_id,),
        )

        rows = db_cursor.fetchall()

        if not rows:
            return json.dumps({})

        first_row = rows[0]
        post = {
            "post_id": first_row["post_id"],
            "title": first_row["title"],
            "publication_date": first_row["publication_date"],
            "image_url": first_row["image_url"],
            "content": first_row["content"],
            "approved": first_row["approved"],
            "user_id": first_row["user_id"],
            "author": first_row["author"],
            "category_id": first_row["category_id"],
            "tags": [],
        }

        for row in rows:
            if row["tag_id"]:
                post["tags"].append({"id": row["tag_id"], "label": row["tag_label"]})

        return json.dumps(post)


def delete_post(post_id):
    """Deletes a post from the database by its id."""
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM Posts
            WHERE id = ?
            """,
            (post_id,),
        )

        conn.commit()


def update_post_tags(post_id, tag_ids):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            DELETE FROM PostTags
            WHERE post_id = ?
        """,
            (post_id,),
        )

        for tag_id in tag_ids:
            db_cursor.execute(
                """
                INSERT INTO PostTags (post_id, tag_id)
                VALUES (?, ?)
            """,
                (post_id, tag_id),
            )

        conn.commit()


def edit_post(pk, post_data):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("SELECT * FROM Posts WHERE id = ?", (pk,))
        existing_post = db_cursor.fetchone()

        if not existing_post:
            return False

        title = post_data.get("title") or existing_post["title"]
        image_url = post_data.get("image_url") or existing_post["image_url"]
        content = post_data.get("content") or existing_post["content"]
        cat_id = (
            post_data.get("category_id")
            or post_data.get("categoryId")
            or existing_post["category_id"]
        )

        approved = existing_post["approved"]
        pub_date = existing_post["publication_date"]

        db_cursor.execute(
            """
            UPDATE Posts
                SET
                    title = ?,
                    image_url = ?,
                    content = ?,
                    category_id = ?,
                    approved = ?,
                    publication_date = ?
            WHERE id = ?
            """,
            (title, image_url, content, cat_id, approved, pub_date, pk),
        )

        # Check if any row was actually updated
        rows_affected = db_cursor.rowcount

        # Always commit changes to the database
        conn.commit()

    return rows_affected > 0

def get_posts_by_subscriptions(follower_id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
            SELECT
                p.id,
                p.title,
                p.publication_date,
                p.content,
                u.username,
                s.follower_id
            FROM Posts p
            JOIN Users u ON p.user_id = u.id
            JOIN Subscriptions s ON s.author_id = p.user_id
            WHERE s.follower_id = ?
            AND s.end_datetime IS NULL
            ORDER BY p.publication_date DESC
        """, (follower_id,))

        posts = []
        dataset = db_cursor.fetchall()
        for row in dataset:
            posts.append(dict(row))
            
    return json.dumps(posts)