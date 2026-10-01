
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

try:
    from langchain_huggingface.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings


def build_retriever(kb_path: str):
    print(f" Loading KB from: {kb_path}")
    
    loader = TextLoader(kb_path)
    documents = loader.load()
    print(f"   Loaded {len(documents)} document(s)")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "###", "##", "\n", " "],
    )
    chunks = splitter.split_documents(documents)
    print(f"   Split into {len(chunks)} chunks")
    
    print("   Building embeddings")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("    KB retriever ready")
    
    return vectorstore.as_retriever(search_kwargs={"k": 3})


def search_kb(retriever, query: str) -> str:
    docs = retriever.invoke(query)
    
    if not docs:
        return "No matching KB articles found. Escalate to appropriate team."
    
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    return context


if __name__ == "__main__":
    print("\n" + "-" * 70)
    print("KB Retriever Test")
    print("-" * 70)
    
    retriever = build_retriever("kb_documents.txt")
    
    test_queries = [
        "VPN keeps disconnecting",
        "Cannot access shared folder",
        "Computer is slow",
    ]
    
    for query in test_queries:
        print(f"\n Query: '{query}'")
        print("-" * 70)
        results = search_kb(retriever, query)
        print(results[:500] + "..." if len(results) > 500 else results)
        print()