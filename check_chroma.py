import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="addiction_coach_docs")

count = collection.count()
print(f"Documents in Chroma: {count}")

if count > 0:
    results = collection.get(limit=3)
    print(f"First 3 docs:")
    for doc in results['documents'] or []:
        print(f"  {doc[:100]}...")
else:
    print("Chroma empty. Run load_pdf.py first.")
