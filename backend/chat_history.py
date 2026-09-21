import sqlite3


DB_PATH = "data/users.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# =========================================================
# CREATE TABLES
# =========================================================

def create_chat_tables():

    connection = get_connection()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # CHAT SESSIONS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # -----------------------------------------------------
    # CHAT MESSAGES TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    connection.commit()

    connection.close()


# =========================================================
# CREATE NEW CHAT SESSION
# =========================================================

def create_chat_session(
    user_id,
    title="New Chat",
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO chat_sessions (
            user_id,
            title
        )
        VALUES (?, ?)
        """,
        (
            user_id,
            title,
        ),
    )


    connection.commit()

    session_id = cursor.lastrowid

    connection.close()


    return session_id


# =========================================================
# GET USER CHAT SESSIONS
# =========================================================

def get_chat_sessions(user_id):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id, title, created_at
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )


    rows = cursor.fetchall()

    connection.close()


    return rows


# =========================================================
# SAVE MESSAGE
# =========================================================

def save_chat_message(
    session_id,
    role,
    content,
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO chat_messages (
            session_id,
            role,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            session_id,
            role,
            content,
        ),
    )


    connection.commit()

    connection.close()


# =========================================================
# GET SESSION MESSAGES
# =========================================================

def get_chat_messages(session_id):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    )


    rows = cursor.fetchall()

    connection.close()


    messages = []

    for role, content in rows:

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )


    return messages


# =========================================================
# UPDATE CHAT TITLE
# =========================================================

def update_chat_title(
    session_id,
    title,
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE chat_sessions
        SET title = ?
        WHERE id = ?
        """,
        (
            title,
            session_id,
        ),
    )


    connection.commit()

    connection.close()