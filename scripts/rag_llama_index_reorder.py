import os
import openai
from llama_index import ServiceContext, SimpleDirectoryReader, VectorStoreIndex, OpenAIEmbedding
from llama_index.llms import OpenAI
from llama_index.postprocessor import LongContextReorder
from llama_index.response.notebook_utils import display_response

# Set the OpenAI API key
openai.api_key = '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'

class LlamaIndexQueryEngine:
    def __init__(self, data_dir, model_name="gpt-3.5-turbo-instruct", temperature=0.1):
        self.data_dir = data_dir
        self.model_name = model_name
        self.temperature = temperature

        self.llm = OpenAI(model=self.model_name, temperature=self.temperature)
        self.ctx = ServiceContext.from_defaults(llm=self.llm, embed_model=OpenAIEmbedding())

        self.documents = self._load_documents()
        self.index = self._create_index()

        # Node Post-processor
        self.reorder = LongContextReorder()
        self.reorder_engine = self.index.as_query_engine(node_postprocessors=[self.reorder], similarity_top_k=5)
        
        self.base_engine = self.index.as_query_engine(similarity_top_k=5)
        
    def _load_documents(self):
        return SimpleDirectoryReader(self.data_dir).load_data()

    def _create_index(self):
        return VectorStoreIndex.from_documents(self.documents, service_context=self.ctx)

    def query_base_engine(self, query):
        response = self.base_engine.query(query)
        display_response(response)
        return response

    def query_reorder_engine(self, query):
        response = self.reorder_engine.query(query)
        display_response(response)
        return response

# if __name__ == "__main__":
#     data_dir = "./data/paul_graham/"
#     query_engine = LlamaIndexQueryEngine(data_dir)

#     query = "Did the author meet Sam Altman?"
#     print("Base Engine Response:")
#     base_response = query_engine.query_base_engine(query)

#     print("\nReorder Engine Response:")
#     reorder_response = query_engine.query_reorder_engine(query)
