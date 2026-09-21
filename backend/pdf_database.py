import os
import sqlite3


DB_PATH = "data/users.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_pdf_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_id TEXT UNIQUE NOT NULL,
            document_name TEXT NOT NULL,
            characters INTEGER DEFAULT 0,
            chunks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_pdf_document(
    user_id,
    document_id,
    document_name,
    characters,
    chunks,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO pdf_documents (
            user_id,
            document_id,
            document_name,
            characters,
            chunks
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            document_id,
            document_name,
            characters,
            chunks,
        ),
    )

    connection.commit()
    connection.close()


def get_user_pdfs(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            document_id,
            document_name,
            characters,
            chunks,
            created_at
        FROM pdf_documents
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    documents = []

    for row in rows:
        documents.append(
            {
                "document_id": row[0],
                "name": row[1],
                "characters": row[2],
                "chunks": row[3],
                "created_at": row[4],
            }
        )

    return documents


def delete_pdf_document(
    user_id,
    document_id,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM pdf_documents
        WHERE user_id = ?
        AND document_id = ?
        """,
        (
            user_id,
            document_id,
        ),
    )

    deleted_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted_rows > 0