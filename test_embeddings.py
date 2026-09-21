from backend.embeddings import get_embeddings


embeddings = get_embeddings()


text = "Python is a programming language."


vector = embeddings.embed_query(text)


print()
print("=" * 60)
print("EMBEDDING TEST")
print("=" * 60)

print("Original Text:")
print(text)

print()
print("Vector Length:")
print(len(vector))

print()
print("First 10 Vector Values:")
print(vector[:10])

print("=" * 60)