import openai
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain.chains import LLMChain, StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_community.document_transformers import LongContextReorder
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
import os

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.environ["OPENAI_API_KEY"]


class LangChainQueryEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir

        # Initialize OpenAIEmbedding
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=openai.api_key
        )
        self.llm = OpenAI()
        self.documents = None
        self.index = None
        self.reorder = LongContextReorder()

        self._load_documents()
        self._create_index()

    def _load_documents(self):
        loader = DirectoryLoader(self.data_dir, show_progress=True)
        docs = loader.load()

        # initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        self.documents = text_splitter.split_documents(docs)

    def _create_index(self):
        # Create an index from the loaded documents
        self.index = Chroma.from_documents(
            self.documents, embedding=self.embeddings
        ).as_retriever(search_kwargs={"k": 10})

    def query_base_engine(self, query):
        # Query using the base engine without reordering
        return self.index.get_relevant_documents(query)

    def query_reorder_engine(self, query):
        # Reorder documents based on relevance and query
        docs = self.index.get_relevant_documents(query)
        reordered_docs = self.reorder.transform_documents(docs)
        return reordered_docs

    def run_query(self, query, reordered=False):
        # Override prompts
        document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )
        document_variable_name = "context"
        stuff_prompt_override = """Given this text extracts:
        -----
        {context}
        -----
        Please answer the following question:
        {query}"""
        prompt = PromptTemplate(
            template=stuff_prompt_override, input_variables=["context", "query"]
        )

        # Instantiate the chain
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name,
        )

        # Choose documents based on whether reordering is required
        input_documents = (
            self.query_reorder_engine(query)
            if reordered
            else self.query_base_engine(query)
        )
        return chain.run(input_documents=input_documents, query=query)


# if __name__ == "__main__":
#     data_dir = "./data/paul_graham/"
#     query_engine = LangChainQueryEngine(data_dir)

#     query = "Did the author meet Sam Altman?"

#     print("Base Engine Response:")
#     base_response = query_engine.run_query(query)
#     print(base_response)

#     print("\nReorder Engine Response:")
#     reorder_response = query_engine.run_query(query, reordered=True)
#     print(reorder_response)
