from backend.router import route_question


print("=" * 60)
print("NOVA AI - INTELLIGENT ROUTER TEST")
print("=" * 60)


questions = [
    "Hi NOVA, how are you?",
    "What is RAG?",
    "Explain Python functions",
    "What is the latest Python version?",
    "What are today's technology news?",
    "According to my uploaded resume, what are my skills?",
]


for question in questions:

    route = route_question(
        question
    )

    print()
    print("Question:")
    print(question)

    print("Route:")
    print(route)

    print("-" * 60)