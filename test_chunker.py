from backend.pdf import read_pdf
from backend.chunker import split_text


file_path = input("Enter PDF path: ")


with open(file_path, "rb") as file:
    text = read_pdf(file)


chunks = split_text(
    text,
    chunk_size=700,
    chunk_overlap=100,
)


print()
print("=" * 60)
print("PDF CHUNKING")
print("=" * 60)

print("Total Characters:", len(text))
print("Total Chunks:", len(chunks))

print("=" * 60)


for index, chunk in enumerate(chunks[:5], start=1):
    print()
    print(f"CHUNK {index}")
    print("-" * 60)
    print(chunk[:300])
    print("-" * 60)