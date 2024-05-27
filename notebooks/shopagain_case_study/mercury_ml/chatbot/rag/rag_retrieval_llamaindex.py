import chromadb
from llama_index import VectorStoreIndex
from llama_index import ServiceContext, LLMPredictor, OpenAIEmbedding, PromptHelper
from llama_index.vector_stores import ChromaVectorStore
from llama_index.llms import OpenAI
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter
from llama_index import StorageContext, load_index_from_storage

class RetrievalRAG():
    def __init__(self, company_id: str, input_dir: str):
        self.company_id = company_id
        self.input_dir = input_dir
        self.documents = None
        self.index = None
        self.query_engine = None
        self.setup()

    def setup(self):
        # Load documents
        self.documents = SimpleDirectoryReader(input_dir=self.input_dir).load_data()

        # Initialize LLM
        conversation_model = OpenAI(model=cfg.openai_api.CONVERSATION_MODEL, temperature=0)

        # https://docs.llamaindex.ai/en/stable/api_reference/service_context/embeddings.html
        embedding_function = OpenAIEmbedding()

        # Initialize Service Context (chunking)
        node_parser = SimpleNodeParser.from_defaults(
            text_splitter=TokenTextSplitter(chunk_size=cfg.rag.CHUNK_SIZE, chunk_overlap=20)
        )

        prompt_helper = PromptHelper(
            context_window=4096,
            num_output=256,
            chunk_overlap_ratio=0.1,
            chunk_size_limit=None
        )

        self.service_context = ServiceContext.from_defaults(
            llm=conversation_model,
            node_parser=node_parser,
            prompt_helper=prompt_helper,
            embed_model=embedding_function,
        )

        # Initialize client, setting path to save data
        db = chromadb.PersistentClient(path=cfg.rag.PERSIST_DIR)

        # Create collection
        chroma_collection = db.get_or_create_collection("quickstart")

        # Assign chroma as the vector_store to the context
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        if self.index is None:
            try:
                self.load_existing_index()
                logging.info("Successfully loaded existing index.")
            except Exception as e:
                logging.debug(f"Exception occurred while loading existing index: {str(e)}. Training new index.")
                self.build_and_persist_index()

        if self.query_engine is None:
            self.initialize_query_engine()                    
                
    def build_and_persist_index(self):
        # Create your index
        self.index = VectorStoreIndex.from_documents(
            self.documents,
            storage_context=self.storage_context,
            service_context=self.service_context
        )

    def load_existing_index(self):
        # Load your index from stored vectors
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            storage_context=self.storage_context
        )

    def initialize_query_engine(self):
        self.query_engine = self.index.as_query_engine(service_context=self.service_context)
        
    def get_response(self, query: str):
        response = self.query_engine.query(query)
        return response
