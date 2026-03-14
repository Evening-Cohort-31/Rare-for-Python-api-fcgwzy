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
            (reaction["emoji"]),
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
            """Select the reaction associated with a particular post
            SELECT 
                pr.id,
                pr.user_id,
                pr.post_id,
                r.label,
                r.emoji
            FROM PostReactions pr
            JOIN Reactions r ON pr.reaction_id = r.id
            WHERE r.post_id = ?
        """,
            (post_id,),
        )

        query_results = db_cursor.fetchall()

        reactions = [dict(row) for row in query_results]
        return json.dumps(reactions)


def add_reaction_to_post(post_reaction):
    """Adds a specific reaction to a post by a user"""
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
                INSERT into PostReactions (user_id, post_id, reaction_id)
                VAlUES (?, ?, ?)
                """,
            post_reaction["user_id"],
            post_reaction["post_id"],
            post_reaction["reaction_id"],
        )

        id = db_cursor.lastrowid
        post_reaction["id"] = id

        return json.dumps(post_reaction)


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
                (updated_reaction["label"], updated_reaction["emoji"], pk)
            )

            rows_affected = db_cursor.rowcount

            return rows_affected > 0

