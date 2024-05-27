import copy
import inspect
from mercury_ml.chatbot.services.product_service import ProductServiceFunctions
from mercury_ml.chatbot.services.order_service import OrderServiceFunctions
from mercury_ml.chatbot.services.shipping_service import ShippingServiceFunctions
from mercury_ml.chatbot.services.return_refund_service import ReturnRefundServiceFunctions
from mercury_ml.chatbot.services.rag_service import RAGServiceFunctions
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

import logging
from mercury_ml.chatbot import config

# initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)

def execute_function_call(company_id, accumulated_info, query, ecom_chatbot=None):
    try:
        function_name = accumulated_info["function_name"]
        arguments = copy.deepcopy(accumulated_info["arguments"])
        arguments['query'] = query
        arguments['company_id'] = company_id
        logging.info(f"execute_function_call::function_name = {function_name}")
        
        # Function mapping for both order-related and product-related functions
        function_map = {
            "get_order_status": OrderServiceFunctions.get_order_status,
            "manage_order_change_request": OrderServiceFunctions.manage_order_change_request,
            "get_public_info": RAGServiceFunctions.get_rag_response,
        }
        
        # Execute the function if it exists in the function_map
        if function_name in function_map:
            # Get the signature of the function to be called
            sig = inspect.signature(function_map[function_name])
    
            # Filter out irrelevant arguments
            filtered_args = {k: v for k, v in arguments.items() if k in sig.parameters}
            logging.debug(f"Filtered arguments: {filtered_args}")
            
            # Assuming df_orders is defined and accessible
            if function_name == "manage_order_request":
                filtered_args["ecom_chatbot"] = ecom_chatbot
            results = function_map[function_name](**filtered_args)
        else:
            results = f"Error: function {function_name} does not exist"
        
        return results
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return str(e)

def user_is_frustrated(probability_list):
    # Check if there are at least 3 elements to compare
    if len(probability_list) < 3:
        return False
    
    # Get the last 3 elements
    last_three = probability_list[-3:]
    
    # Check if they are consecutively increasing
    # if last_three[0] < last_three[1] < last_three[2]:
    
    # Check if the last element is greater than 0.7    
    if last_three[2] > 0.7:
        return True
    
    return False
