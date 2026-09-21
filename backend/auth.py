import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


DB_PATH = "data/users.db"


# --------------------------------
# Database connection
# --------------------------------

def get_connection():

    return sqlite3.connect(DB_PATH)


# --------------------------------
# Create users table
# --------------------------------

def create_users_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


# --------------------------------
# Register user
# --------------------------------

def register_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    hashed_password = generate_password_hash(
        password
    )

    try:

        cursor.execute(
            """
            INSERT INTO users (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                username,
                hashed_password,
            ),
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# --------------------------------
# Login user
# --------------------------------

def login_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, password
        FROM users
        WHERE username = ?
        """,
        (username,),
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:

        return None

    user_id = user[0]
    username = user[1]
    stored_password = user[2]

    password_correct = check_password_hash(
        stored_password,
        password,
    )

    if password_correct:

        return {
            "id": user_id,
            "username": username,
        }

    return None