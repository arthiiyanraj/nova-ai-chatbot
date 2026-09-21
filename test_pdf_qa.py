from backend.pdf_qa import ask_pdf


question = input(
    "Ask a question about the PDF: "
)


print()
print("NOVA is searching the PDF...")
print()


answer = ask_pdf(
    question,
    top_k=3,
)


print("=" * 60)
print("NOVA ANSWER")
print("=" * 60)

print(answer)

print("=" * 60)