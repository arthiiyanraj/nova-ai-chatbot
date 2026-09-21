import sqlite3


DB_PATH = "data/users.db"


def get_connection():

    return sqlite3.connect(DB_PATH)


# --------------------------------
# Create memory table
# --------------------------------

def create_memory_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memory TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


# --------------------------------
# Save memory
# --------------------------------

def save_memory(user_id, memory):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories (user_id, memory)
        VALUES (?, ?)
        """,
        (
            user_id,
            memory,
        ),
    )

    connection.commit()
    connection.close()


# --------------------------------
# Get memories
# --------------------------------

def get_memories(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT memory
        FROM memories
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 20
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        row[0]
        for row in rows
    ]


# --------------------------------
# Build current chat history
# --------------------------------

def build_chat_history(messages):

    history = []

    for message in messages:

        role = message["role"]
        content = message["content"]

        history.append(
            (
                role,
                content,
            )
        )

    return history


# --------------------------------
# Detect useful user information
# --------------------------------

def detect_memory(text):

    text = text.strip()

    lower_text = text.lower()

    memory_patterns = [
        "my name is ",
        "i am learning ",
        "i like ",
        "i love ",
        "my hobby is ",
        "i work as ",
        "i am working as ",
    ]

    for pattern in memory_patterns:

        if lower_text.startswith(pattern):

            return text

    return None