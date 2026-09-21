def split_text(text, chunk_size=700, chunk_overlap=100):
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks