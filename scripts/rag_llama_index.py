import os
import chromadb

from llama_index.llms import OpenAI
from llama_index.vector_stores import ChromaVectorStore
from llama_index.text_splitter import SentenceSplitter
from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    ServiceContext,
    OpenAIEmbedding,
    get_response_synthesizer,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import (
    SimilarityPostprocessor,
    SentenceEmbeddingOptimizer,
)

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.environ["OPENAI_API_KEY"]


class RAGLlamaIndex:
    def __init__(self, input_dir: str, persist_dir: str):
        self.input_dir = input_dir
        self.persist_dir = persist_dir

        self.documents = None
        self.index = None
        self.query_engine = None
        self.setup()

    def setup(self):
        # Load documents
        self.documents = SimpleDirectoryReader(
            input_dir=self.input_dir, exclude_hidden=False
        ).load_data()
        # print("self.documents = ",self.documents)

        # Initialize LLM
        conversation_model = OpenAI(model="gpt-3.5-turbo-0613", temperature=0.2)

        # https://docs.llamaindex.ai/en/stable/api_reference/service_context/embeddings.html
        embedding_function = OpenAIEmbedding()

        # Initialize Service Context (chunking)
        node_parser = SentenceSplitter(chunk_size=500, chunk_overlap=100)

        self.service_context = ServiceContext.from_defaults(
            llm=conversation_model,
            node_parser=node_parser,
            embed_model=embedding_function,
        )

        # Initialize client, setting path to save data
        db = chromadb.PersistentClient(path=self.persist_dir)

        # Create collection
        chroma_collection = db.get_or_create_collection("quickstart")

        # Assign chroma as the vector_store to the context
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        if self.index is None:
            try:
                self.load_existing_index()
                print("Successfully loaded existing index.")
            except Exception as e:
                print(
                    f"Exception occurred while loading existing index: {str(e)}. Training new index."
                )
                self.build_and_persist_index()

        # configure vector_retriever
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=5,
        )

        # configure response synthesizer
        self.response_synthesizer = get_response_synthesizer()

        if self.query_engine is None:
            self.initialize_query_engine()

    def build_and_persist_index(self):
        # Create your index
        self.index = VectorStoreIndex.from_documents(
            self.documents,
            storage_context=self.storage_context,
            service_context=self.service_context,
        )
        # persist index
        self.index.storage_context.persist(self.persist_dir)

    def load_existing_index(self):
        db2 = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db2.get_or_create_collection("quickstart")
        count = chroma_collection.count()
        print(f"Collection count: {count}")

        # Check if the count is zero and raise an exception if true
        if count == 0:
            print("Empty index")
            raise Exception("Empty index")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store,
            service_context=self.service_context,
        )

    def initialize_query_engine(self):
        # assemble query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=self.response_synthesizer,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.5),
                SentenceEmbeddingOptimizer(
                    embed_model=self.service_context.embed_model, percentile_cutoff=0.5
                ),  # threshold_cutoff=0.7)
            ],
        )

    def get_response_context_with_scores(self, query: str):
        """
        Process the query and return node texts and their scores.
        """
        response = self.get_response(query)
        return [
            (node_with_score.node.text, node_with_score.score)
            for node_with_score in response.source_nodes
        ]

    def get_response_context(self, query: str):
        """
        Process the query and return only node texts.
        """
        response = self.get_response(query)
        return [node_with_score.node.text for node_with_score in response.source_nodes]

    def get_response(self, query: str):
        response = self.query_engine.query(query)
        return response


# if __name__ == "__main__":
#     rag = RetrievalRAG()
#     response = rag.get_response("How do you ship?")
#     print("response = ",response)

#     # print("response nodes = ",response.source_nodes)

#     for node_with_score in response.source_nodes:
#         node = node_with_score.node
#         score = node_with_score.score

#         node_id = node.id_
#         node_text = node.text
#         node_metadata = node.metadata

#         print(f"Node ID: {node_id}")
#         print(f"Node Score: {score}")
#         print(f"Node Text: {node_text[:100]}...")  # print first 100 characters of the node text for brevity
#         print("Node Metadata:")
#         for key, value in node_metadata.items():
#             print(f"  {key}: {value}")
#         print("\n")
