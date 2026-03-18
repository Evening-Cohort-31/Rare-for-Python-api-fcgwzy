import sqlite3
import json
from datetime import datetime


def login_user(user):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            select id, username, is_admin, active
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
                "active": user_from_db["active"],
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


def count_admin_users():
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT COUNT(*)
            FROM Users
            WHERE is_admin = 1 and active = 1
        """
        )

        return db_cursor.fetchone()[0]


def process_admin_demotion(admin_id, action, approver_id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT * FROM DemotionQueue
            WHERE admin_id = ? and action = ?
        """,
            (admin_id, action),
        )

        pending = db_cursor.fetchone()

        if pending is None:
            db_cursor.execute(
                """
                INSERT INTO DemotionQueue (action, admin_id, approver_one_id)
                VALUES (?, ?, ?)
            """,
                (action, admin_id, approver_id),
            )

            conn.commit()

            return {
                "pending": True,
                "message": "First admin approved, pending second admin approval.",
            }

        if pending["approver_one_id"] == approver_id:
            return {"error": "You have already given approval."}

        if action == "deactivate":
            db_cursor.execute("UPDATE Users SET active = 0 WHERE id = ?", (admin_id,))

        if action == "demote":
            db_cursor.execute("UPDATE Users SET is_admin = 0 WHERE id = ?", (admin_id,))

        db_cursor.execute(
            """
            DELETE FROM DemotionQueue
            WHERE admin_id = ? and action = ?
        """,
            (admin_id, action),
        )

        conn.commit()

        return {"message": "Second admin approval. Action completed."}


def update_user(user_id, user_data, requested_by):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()
        admin_count = count_admin_users()

        db_cursor.execute("SELECT is_admin, active FROM Users WHERE id = ?", (user_id,))
        current_user = db_cursor.fetchone()

        if current_user is None:
            return {"error": "User not found"}

        new_is_admin = user_data.get("is_admin", current_user["is_admin"])

        new_active = user_data.get("active", current_user["active"])

        if current_user["is_admin"] == 1 and admin_count == 1:
            if new_is_admin == 0 or new_active == 0:
                return {
                    "error": "You must assign another admin before removing or deactivating the last admin."
                }

        if current_user["is_admin"] == 0 and new_is_admin == 1:
            action = "promote"

            if admin_count == 1:
                db_cursor.execute(
                    """
                    UPDATE Users
                    SET is_admin = ?, active = ?
                    WHERE id = ?
                """,
                    (new_is_admin, new_active, user_id),
                )

                conn.commit()

                return True

            db_cursor.execute(
                """
            SELECT * FROM DemotionQueue
            WHERE admin_id = ? AND action = ?
            """,
                (user_id, action),
            )

            pending = db_cursor.fetchone()

            if pending is None:
                db_cursor.execute(
                    """
                    INSERT INTO DemotionQueue (action, admin_id, approver_one_id)
                    VALUES (?, ?, ?)
                    """,
                    (action, user_id, requested_by),
                )

                conn.commit()

                return {
                    "pending": True,
                    "message": "First admin approved, pending second admin approval.",
                }
            if pending["approver_one_id"] == requested_by:
                return {"error": "You have already approved this action."}

            db_cursor.execute(
                "UPDATE Users SET is_admin = 1 WHERE id = ?",
                (user_id,),
            )

            db_cursor.execute(
                """
                DELETE FROM DemotionQueue
                WHERE admin_id = ? AND action = ?
                """,
                (user_id, action),
            )

            conn.commit()

            return {"message": "Second admin approval, action completed."}

        if current_user["is_admin"] == 1:
            if new_active == 0:
                action = "deactivate"
            elif new_is_admin == 0:
                action = "demote"
            else:
                action = None

            if action:
                db_cursor.execute(
                    """
                    SELECT * FROM DemotionQueue
                                  WHERE admin_id = ? AND action = ?
                """,
                    (user_id, action),
                )
                pending = db_cursor.fetchone()

                if pending is None:
                    db_cursor.execute(
                        """
                        INSERT INTO DemotionQueue (action, admin_id, approver_one_id)
                        VALUES (?, ?, ?)
                    """,
                        (action, user_id, requested_by),
                    )
                    conn.commit()
                    return {
                        "pending": True,
                        "message": "First admin approved, pending second admin approval.",
                    }

                if pending["approver_one_id"] == requested_by:
                    return {"error": "You have already approved this action."}

                if action == "deactivate":
                    db_cursor.execute(
                        "UPDATE Users SET active = 0 WHERE id = ?", (user_id,)
                    )
                elif action == "demote":
                    db_cursor.execute(
                        "UPDATE Users SET is_admin = 0 WHERE id = ?", (user_id,)
                    )

                db_cursor.execute(
                    """
                    DELETE FROM DemotionQueue
                    WHERE admin_id = ? AND action = ?
                """,
                    (user_id, action),
                )

                conn.commit()
                return {"message": "Second admin approval, action completed."}

        db_cursor.execute(
            """
            UPDATE Users
            SET 
                is_admin = ?,
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

        conn.commit()

        return db_cursor.rowcount > 0
