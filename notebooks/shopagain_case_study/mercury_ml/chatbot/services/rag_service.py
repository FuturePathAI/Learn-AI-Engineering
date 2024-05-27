import logging
from typing import Tuple, Optional
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.shopagain import fetch_order_info, fetch_order_info_by_user
from mercury_ml.chatbot.utils.service_utils import process_product_return, process_product_replacement
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)
    
class RAGServiceFunctions:
    @staticmethod
    def get_rag_response(company_id: str, query: str) -> Tuple[str, str]:
        """Get the return policy of the company.
            Returns: (status_message, next_step)
        """
        try:
            # Retrieve the return policy using RAG
            rag = get_or_create_rag(company_id)
            response = rag.get_response(f"{query}")
            
            # Assuming the response contains the return policy
            if response:
                return f"{response['output_text']}", ""
            else:
                return "Unable to retrieve the return policy at the moment.", "Please try again later."
        except Exception as e:
            logging.exception(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"