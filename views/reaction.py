import sqlite3
import json


def create_reaction(reaction):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()
        db_cursor.execute(
            """
        INSERT into Reactions (label, emoji) values (?, ?)

        """,
            (reaction["label"], reaction["emoji"]),
        )

        id = db_cursor.lastrowid

        return json.dumps({"id": id, "emoji": reaction["emoji"]})


def get_all_reactions():
    """Returns every existing reaction type on the app"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """ 
            SELECT id, label, emoji FROM Reactions
        """
        )

        query_results = db_cursor.fetchall()
        reactions = [dict(row) for row in query_results]
        return json.dumps(reactions)


def get_all_reactions_for_post(post_id):
    """Returns all reactions that have been applied to a specific post"""
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
                    SELECT 
                        r.id,
                        r.label,
                        r.emoji,
                        COUNT(pr.id) as count
                    FROM Reactions r
                    LEFT JOIN PostReactions pr 
                        ON r.id = pr.reaction_id AND pr.post_id = ?
                    GROUP BY r.id
                """,
            (post_id,),
        )

        query_results = db_cursor.fetchall()
        reactions = [dict(row) for row in query_results]
        return json.dumps(reactions)


def add_reaction_to_post(post_reaction):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row  # This makes existing_reaction['id'] work
        db_cursor = conn.cursor()

        u_id = int(post_reaction["user_id"])
        p_id = int(post_reaction["post_id"])
        r_id = int(post_reaction["reaction_id"])

        db_cursor.execute(
            """
            SELECT id FROM PostReactions 
            WHERE user_id = ? AND post_id = ? AND reaction_id = ?
            """,
            (u_id, p_id, r_id)
        )
        existing_reaction = db_cursor.fetchone()

        if existing_reaction:
            # Step 2: If found, only delete that specific row
            db_cursor.execute(
                "DELETE FROM PostReactions WHERE id = ?", (existing_reaction["id"],)
            )
            post_reaction["action"] = "removed"
        else:
            # Step 3: If not found, add a new one for this user
            db_cursor.execute(
                """INSERT INTO PostReactions (user_id, post_id, reaction_id)
                VALUES (?, ?, ?)""",
                (
                    post_reaction["user_id"],
                    post_reaction["post_id"],
                    post_reaction["reaction_id"],
                ),
            )
            post_reaction["action"] = "added"

        conn.commit()
        return json.dumps(post_reaction)


def delete_reaction(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()
        db_cursor.execute("DELETE FROM Reactions WHERE id = ?", (id,))
        return db_cursor.rowcount > 0


def delete_post_reaction(id):
    """Removes a user's reaction from a post"""
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """DELETE from PostReactions
            WHERE id = ? """,
            (id,),
        )

        rows_affected = db_cursor.rowcount

        return rows_affected > 0


def update_reaction(pk, updated_reaction):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
                UPDATE Reactions
                SET 
                    label = ?,
                    emoji = ?
                WHERE id = ?
                """,
            (updated_reaction["label"], updated_reaction["emoji"], pk),
        )

        rows_affected = db_cursor.rowcount

        return rows_affected > 0
