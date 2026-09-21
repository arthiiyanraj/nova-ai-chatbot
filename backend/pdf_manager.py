import uuid

from backend.pdf import read_pdf
from backend.chunker import split_text
from backend.vectorstore import create_vector_store


def process_pdf(
    uploaded_file,
    user_id,
):

    # ========================================================
    # READ PDF
    # ========================================================

    try:

        pdf_text = read_pdf(
            uploaded_file
        )

    except Exception as error:

        return {
            "success": False,
            "message": (
                f"Unable to read the PDF: {error}"
            ),
            "characters": 0,
            "chunks": 0,
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    # ========================================================
    # CHECK TEXT
    # ========================================================

    if not pdf_text.strip():

        return {
            "success": False,
            "message": (
                "The PDF was opened successfully, "
                "but no readable text was found."
            ),
            "characters": 0,
            "chunks": 0,
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    # ========================================================
    # SPLIT TEXT INTO CHUNKS
    # ========================================================

    chunks = split_text(
        pdf_text,
        chunk_size=700,
        chunk_overlap=100,
    )

    # ========================================================
    # CHECK CHUNKS
    # ========================================================

    if not chunks:

        return {
            "success": False,
            "message": (
                "The PDF contains text, "
                "but no usable chunks were created."
            ),
            "characters": len(pdf_text),
            "chunks": 0,
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    # ========================================================
    # CREATE DOCUMENT ID
    # ========================================================

    document_id = str(
        uuid.uuid4()
    )

    # ========================================================
    # CREATE VECTOR STORE
    # ========================================================

    try:

        create_vector_store(
            chunks,
            user_id,
            document_id,
        )

    except Exception as error:

        return {
            "success": False,
            "message": (
                f"Failed to create PDF knowledge base: {error}"
            ),
            "characters": len(pdf_text),
            "chunks": len(chunks),
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    # ========================================================
    # SUCCESS
    # ========================================================

    return {
        "success": True,
        "message": (
            "PDF processed successfully."
        ),
        "characters": len(pdf_text),
        "chunks": len(chunks),
        "document_id": document_id,
        "document_name": uploaded_file.name,
    }