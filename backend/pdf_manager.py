import uuid

from backend.pdf import read_pdf
from backend.chunker import split_text
from backend.vectorstore import create_vector_store


def process_pdf(
    uploaded_file,
    user_id,
):

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

    pdf_text = pdf_text.strip()

    if not pdf_text:

        return {
            "success": False,
            "message": (
                "The PDF was opened successfully, "
                "but no readable text was found. "
                "This may be a scanned/image-only PDF."
            ),
            "characters": 0,
            "chunks": 0,
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    chunks = split_text(
        pdf_text,
        chunk_size=700,
        chunk_overlap=100,
    )

    if not chunks:

        return {
            "success": False,
            "message": (
                "No usable text chunks were created."
            ),
            "characters": len(pdf_text),
            "chunks": 0,
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    document_id = str(
        uuid.uuid4()
    )

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
                "Failed to create the PDF "
                f"knowledge base: {error}"
            ),
            "characters": len(pdf_text),
            "chunks": len(chunks),
            "document_id": None,
            "document_name": uploaded_file.name,
        }

    return {
        "success": True,
        "message": "PDF processed successfully.",
        "characters": len(pdf_text),
        "chunks": len(chunks),
        "document_id": document_id,
        "document_name": uploaded_file.name,
    }