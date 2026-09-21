from io import BytesIO

from pypdf import PdfReader


def read_pdf(file):

    # ========================================================
    # READ UPLOADED FILE AS BYTES
    # ========================================================

    try:
        file_bytes = file.getvalue()
    except AttributeError:
        file_bytes = file.read()

    # ========================================================
    # CHECK EMPTY FILE
    # ========================================================

    if not file_bytes:
        raise ValueError(
            "The uploaded PDF is empty. "
            "Please choose the PDF again."
        )

    # ========================================================
    # CREATE A NEW MEMORY STREAM
    # ========================================================

    pdf_stream = BytesIO(file_bytes)

    # ========================================================
    # READ PDF
    # ========================================================

    reader = PdfReader(pdf_stream)

    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    text_parts = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text_parts.append(
                page_text
            )

    # ========================================================
    # COMBINE ALL PAGES
    # ========================================================

    text = "\n\n".join(
        text_parts
    )

    return text