import sqlite3
import json
from datetime import datetime

def create_post(post):
    """Adds a post to the database when they register

    Args:
        post (dictionary): The dictionary passed to the register post request

    Returns:
        json string: Contains the token of the newly created post
    """
    with sqlite3.connect('./db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        Insert into Posts (user_id, category_id, title, publication_date, image_url, content, approved) values (?, ?, ?, ?, ?, ?, ?)
        """, (
            post['user_id'],
            post['category_id'],
            post['title'],
            datetime.now(),
            post['image_url'],
            post['content'],
            post['approved']
            
        ))

        id = db_cursor.lastrowid

        return json.dumps({
            'token': id,
            'valid': True
        })

def get_all_posts():
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute(
                    """
                    SELECT
                        p.id,
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
                """
                )

        query_results = db_cursor.fetchall()

        posts = []

        for row in query_results:
            posts.append(dict(row))

        return json.dumps(posts)

def get_single_users_post(user_id): # Pass the ID directly, not a dict
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
        posts = [dict(row) for row in dataset] # Convert all rows to dicts
        
        return json.dumps(posts)