import sqlite3
import json
from datetime import datetime


def login_user(user):
    """Checks for the user in the database

    Args:
        user (dict): Contains the username and password of the user trying to login

    Returns:
        json string: If the user was found will return valid boolean of True and the user's id as the token
                     If the user was not found will return valid boolean False
    """
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
    """Adds a user to the database when they register

    Args:
        user (dictionary): The dictionary passed to the register post request

    Returns:
        json string: Contains the token of the newly created user
    """
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

        # We join the tables so we get names/prices instead of just ID numbers
        db_cursor.execute(
            """
            SELECT
                u.first_name,
                u.last_name,
                u.email,
                u.username,
                u.password,
                u.bio,
                u.created_on,
                u.active
            FROM Users u               
        """
        )

        query_results = db_cursor.fetchall()

        users = []

        for row in query_results:
            users.append(dict(row))

        return json.dumps(users)


def user_is_admin(user_id):
    print("incoming user_id:", user_id)
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        print("Failed to convert to int")
        return False
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
        print("is_admin value:", user["is_admin"])
        return user["is_admin"] == 1
