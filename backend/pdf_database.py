import sqlite3


# ============================================================
# DATABASE PATH
# ============================================================

DB_PATH = "data/users.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# ============================================================
# CREATE PDF TABLE
# ============================================================

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


# ============================================================
# SAVE PDF
# ============================================================

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


# ============================================================
# GET USER PDFs
# ============================================================

def get_user_pdfs(
    user_id,
):

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


# ============================================================
# DELETE PDF METADATA
# ============================================================

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