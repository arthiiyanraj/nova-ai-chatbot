from backend.retriever import search_pdf


question = input("Ask a question about the PDF: ")


documents = search_pdf(
    question,
    top_k=3,
)


print()
print("=" * 60)
print("RETRIEVED PDF CHUNKS")
print("=" * 60)


for index, document in enumerate(
    documents,
    start=1,
):
    print()
    print(f"CHUNK {index}")
    print("-" * 60)
    print(document.page_content)
    print("-" * 60)