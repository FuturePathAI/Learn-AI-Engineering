import os
import openai

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.environ["OPENAI_API_KEY"]


class RAGLangchain:
    def __init__(self, input_dir: str, persist_dir: str):
        self.input_dir = input_dir
        self.persist_dir = persist_dir

        self.db = None
        self.chain = None
        self.chunks = None

        # Initialize OpenAIEmbedding
        self.embedding_function = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=openai.api_key
        )
        # Call the setup method
        self.setup()

    def setup(self):
        self.train_index()
        if self.db is None:
            try:
                self.load_existing_index()
                print("Successfully loaded existing index.")
            except Exception as e:
                print(
                    f"Exception occurred while loading existing index: {str(e)}. Training new index."
                )
                self.train_index()

        if self.chain is None:
            self.initialize_chain()

    def train_index(self):
        self.load_and_chunk_data()
        self.build_and_persist_index()

    def load_and_chunk_data(self):
        loader = DirectoryLoader(self.input_dir, show_progress=True)
        docs = loader.load()
        # print("docs = ",docs)

        # initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        self.chunks = text_splitter.split_documents(docs)

    def build_and_persist_index(self):
        # Create in-memory embedding database and save it
        self.db = Chroma.from_documents(
            self.chunks, self.embedding_function, persist_directory=self.persist_dir
        )

    def load_existing_index(self):
        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_function,
        )

    def initialize_chain(self):
        self.chain = load_qa_chain(
            ChatOpenAI(
                temperature=0.2, model_name="gpt-4", openai_api_key=openai.api_key
            ),
            chain_type="stuff",
        )

    def get_response(self, query: str, return_context=False):
        # print(f"Received query: {query}")

        docs = self.db.similarity_search(query)
        if return_context:
            return docs

        return self.chain(
            {"input_documents": docs, "question": query}, return_only_outputs=True
        )
