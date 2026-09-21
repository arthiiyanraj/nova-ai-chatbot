from backend.pdf_manager import process_pdf


file_path = input("Enter PDF path: ")


with open(file_path, "rb") as file:
    result = process_pdf(file)


print()
print("=" * 60)
print("PDF PROCESSING RESULT")
print("=" * 60)

print("Success:", result["success"])
print("Message:", result["message"])
print("Characters:", result["characters"])
print("Chunks:", result["chunks"])

print("=" * 60)