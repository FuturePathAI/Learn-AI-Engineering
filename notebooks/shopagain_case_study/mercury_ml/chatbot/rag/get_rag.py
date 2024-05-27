from mercury_ml.chatbot.rag.rag_retrieval import RetrievalRAG

cid2rag = {}

def get_or_create_rag(company_id):
    if company_id not in cid2rag:
        cid2rag[company_id] = RetrievalRAG(company_id)
    return cid2rag[company_id]
