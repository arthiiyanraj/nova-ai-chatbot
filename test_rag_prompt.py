from backend.rag_prompt import create_rag_prompt


prompt = create_rag_prompt()


context = """
Python, SQL, and Java are mentioned in the document.

The user has completed B.E. Computer Science Engineering.
"""


question = "What programming languages are mentioned?"


messages = prompt.invoke(
    {
        "context": context,
        "question": question,
    }
)


print()
print("=" * 60)
print("RAG PROMPT TEST")
print("=" * 60)

for message in messages.messages:
    print()
    print("ROLE:", message.type)
    print("CONTENT:")
    print(message.content)

print("=" * 60)