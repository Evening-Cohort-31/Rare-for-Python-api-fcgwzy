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
        Insert into Posts (user_id, category_id, title, publication_date, image_url, content, approved) values (?, ?, ?, ?, ?, ?, ?, 1)
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

def get_all_posts(query_params):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute("""
            SELECT
                *
            FROM Posts u               
        """)

        query_results = db_cursor.fetchall()

        posts = []

        for row in query_results:
            posts.append(dict(row))

        return json.dumps(posts)

def get_single_users_post(post_data):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? as a placeholder to prevent SQL injection
        db_cursor.execute(""" 
            SELECT
                *
            FROM Posts p
            WHERE p.user_id = ?
            """, (post_data['user_id'],))
        
        data = db_cursor.fetchone()

        if data:
            return json.dumps(dict(data))
        
        return None