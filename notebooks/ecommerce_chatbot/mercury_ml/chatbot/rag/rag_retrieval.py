import os
import logging
from threading import Lock

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI

from mercury_ml.chatbot import config
# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)
        
class RetrievalRAG():
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.db = None
        self.chain = None
        self.chunks = None
        self.KNOWLEDGE_BASE_DIR = os.path.join(cfg.rag.KNOWLEDGE_BASE_DIR, company_id)
        self.PERSIST_DIR = os.path.join(cfg.rag.PERSIST_DIR, company_id)

        logging.info(self.KNOWLEDGE_BASE_DIR)
        logging.info(self.PERSIST_DIR)
            

        # Initialize OpenAIEmbedding
        self.embedding_function = OpenAIEmbeddings(model=cfg.rag.EMBEDDING_MODEL,
                                                   openai_api_key=cfg.openai_api.API_KEY)
        # Call the setup method
        self.setup()

    def setup(self):
        self.train_index()
        if self.db is None:
            try:
                self.load_existing_index()
                logging.info("Successfully loaded existing index.")
            except Exception as e:
                logging.debug(f"Exception occurred while loading existing index: {str(e)}. Training new index.")
                self.train_index()
        
        if self.chain is None:
            self.initialize_chain()
            
    def train_index(self):
        self.load_and_chunk_data()
        self.build_and_persist_index()
        
    def load_and_chunk_data(self):
        loader = DirectoryLoader(self.KNOWLEDGE_BASE_DIR, show_progress=True)
        docs = loader.load()
        print("docs = ",docs)
        
        # initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=cfg.rag.CHUNK_SIZE, chunk_overlap=cfg.rag.CHUNK_OVERLAP)
        self.chunks = text_splitter.split_documents(docs)

    def build_and_persist_index(self):
        # Create in-memory embedding database and save it
        self.db = Chroma.from_documents(self.chunks, 
                                        self.embedding_function, 
                                        persist_directory=self.PERSIST_DIR)

    def load_existing_index(self):
        self.db = Chroma(persist_directory=self.PERSIST_DIR, 
                         embedding_function=self.embedding_function)

    def initialize_chain(self):
        self.chain = load_qa_chain(ChatOpenAI(temperature=cfg.rag.OPENAI_TEMPERATURE,
                                              model_name=cfg.rag.CONVERSATION_MODEL,
                                              openai_api_key=cfg.openai_api.API_KEY),
                                   chain_type="stuff")

    def get_response(self, query: str):
        logging.debug(f"Received query: {query}")
                
        docs = self.db.similarity_search(query)
        return self.chain({"input_documents": docs, "question": query}, return_only_outputs=True)
