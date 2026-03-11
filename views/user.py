import sqlite3
import json
from datetime import datetime


def login_user(user):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            select id, username, is_admin
            from Users
            where username = ?
            and password = ?
        """,
            (user["username"], user["password"]),
        )

        user_from_db = db_cursor.fetchone()

        if user_from_db is not None:
            response = {
                "valid": True,
                "token": user_from_db["id"],
                "is_admin": user_from_db["is_admin"],
            }
        else:
            response = {"valid": False}

        return json.dumps(response)


def create_user(user):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        Insert into Users (first_name, last_name, username, email, password, bio, created_on, active, is_admin) values (?, ?, ?, ?, ?, ?, ?, 1, 0)
        """,
            (
                user["first_name"],
                user["last_name"],
                user["username"],
                user["email"],
                user["password"],
                user["bio"],
                datetime.now(),
            ),
        )

        id = db_cursor.lastrowid

        return json.dumps({"token": id, "valid": True, "is_admin": 0})

def get_all_users(query_params):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                u.email,
                u.username,
                u.bio,
                u.created_on,
                u.active,
                u.is_admin,
                u.profile_image_url
            FROM Users u               
        """
        )

        query_results = db_cursor.fetchall()

        users = []

        for row in query_results:
            users.append(dict(row))

        return json.dumps(users)

def get_user_by_id(user_id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT
                u.id,
                u.first_name,
                u.last_name,
                u.email,
                u.username,
                u.bio,
                u.created_on,
                u.active,
                u.is_admin,
                u.profile_image_url
            FROM Users u
            WHERE u.id = ?
        """,
            (user_id,),
        )

        user = db_cursor.fetchone()

        if user is None:
            return json.dumps({})

        return json.dumps(dict(user))


def user_is_admin(user_id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT is_admin
            FROM Users
            WHERE id = ?
        """,
            (user_id,),
        )

        user = db_cursor.fetchone()

        if user is None:
            return False

        return user["is_admin"] == 1


def update_user(user_id, user_data):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("SELECT is_admin, active FROM Users WHERE id = ?", (user_id,))
        current_user = db_cursor.fetchone()

        if current_user is None:
            return False
        
        new_is_admin = user_data["is_admin"] if "is_admin" in user_data else current_user["is_admin"]
        new_active = user_data["active"] if "active" in user_data else current_user["active"]

        db_cursor.execute(
            """
            UPDATE Users
            SET is_admin = ?,
            active = ?
            WHERE id = ?
            """,
            (new_is_admin, new_active, user_id),
        )

        conn.commit()
        return db_cursor.rowcount > 0


def update_user_avatar(user_id, user_data):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Users
            SET profile_image_url = ?
            WHERE id = ?
            """,
            (user_data["profile_image_url"], user_id),
        )

        return db_cursor.rowcount > 0