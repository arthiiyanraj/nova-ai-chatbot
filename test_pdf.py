from backend.pdf import read_pdf


file_path = input("Enter PDF path: ")


with open(file_path, "rb") as file:

    text = read_pdf(file)


print("\n")
print("=" * 60)
print("PDF TEXT")
print("=" * 60)

print(text[:3000])

print("=" * 60)

print("Characters:", len(text))