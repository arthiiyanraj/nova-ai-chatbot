from backend.pdf import read_pdf
from backend.chunker import split_text
from backend.vectorstore import create_vector_store


file_path = input("Enter PDF path: ")


with open(file_path, "rb") as file:
    text = read_pdf(file)


chunks = split_text(
    text,
    chunk_size=700,
    chunk_overlap=100,
)


print()
print("Creating ChromaDB...")


vector_store = create_vector_store(chunks)


print()
print("=" * 60)
print("CHROMADB TEST")
print("=" * 60)

print("Total Characters:", len(text))
print("Total Chunks:", len(chunks))
print("Vector Store: Created")
print("Database Path: ./data/chroma_db")

print("=" * 60)