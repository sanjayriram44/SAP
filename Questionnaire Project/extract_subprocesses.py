# extract_subprocesses.py

from core.models import llm_instance
from vector_utils import load_documents, create_or_load_vectorstore

NUM_SUBPROCESS_DOCS = 5

def extract_subprocesses():
    """Uses RAG + LLM to extract subprocess names from sourcing documents."""
    documents = load_documents()
    vectorstore = create_or_load_vectorstore(documents)
    retriever = vectorstore.as_retriever(search_kwargs={"k": NUM_SUBPROCESS_DOCS})

    query = "List the key subprocesses involved in an SAP Ariba Sourcing project."
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    extraction_prompt = f"""
You are a senior SAP consultant. Based on the following content from SAP Ariba Sourcing documents,
identify the 10 most critical subprocesses involved in the sourcing lifecycle.

Return a clean, numbered list. For example, subprocess names could be like:
•	Sourcing Request Creation
•	Sourcing Project Setup (Full/Quick Project)
•	Event Configuration (RFI/RFP/Auction)
•	Template Selection and Rule Definition
•	Supplier Invitation and Enablement
•	Event Publishing and Supplier Communication
•	Supplier Response Submission
•	Bid Evaluation and Award Scenario Creation
•	Approval Workflow for Publish and Award
•	Reporting, Compliance, and Performance Monitoring


Do not provide descriptions or explanations.

--- CONTEXT START ---
{context}
--- CONTEXT END ---
"""

    response = llm_instance.invoke(extraction_prompt)

    subprocesses = [
        line.strip().lstrip("0123456789.- ").strip()
        for line in response.content.strip().split("\n")
        if line.strip()
    ]
    return subprocesses

if __name__ == "__main__":
    subprocesses = extract_subprocesses()
    print("✅ Extracted Subprocesses:")
    for idx, sp in enumerate(subprocesses, 1):
        print(f"{idx}. {sp}")
