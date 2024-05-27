import logging
from typing import Tuple, Optional
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.shopagain import fetch_order_info, fetch_order_info_by_user
from mercury_ml.chatbot.utils.service_utils import format_order_status_string
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)

class ShippingServiceFunctions:
    @staticmethod
    def get_shipping_policy(company_id: str, query: str) -> Tuple[str, str]:
        """Get the shipping policy of the company.
            Returns: (status_message, next_step)
        """
        try:
            # Retrieve the shipping policy using chat engine
            rag = get_or_create_rag(company_id)
            response = rag.get_response(f"{query}")
            
            if response:
                return f"{response['output_text']}", ""
            else:
                return "Unable to retrieve the shipping policy at the moment.", "Please try again later."
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_shipping_status(company_id: str, 
                            order_id: Optional[int] = None, 
                            email: Optional[str] = None, 
                            mobile: Optional[str] = None) -> Tuple[str, str]:
        try:
            if order_id is not None:
                shipping_info = fetch_order_info(str(company_id, order_id))
            elif email is not None:
                shipping_info = fetch_order_info_by_user(company_id, email=email)
            elif mobile is not None:
                shipping_info = fetch_order_info_by_user(company_id, mobile=mobile)
            else:
                return "", "Could you please provide the Order ID, email, or phone number?"
            
            if 'order_status' in shipping_info:
                return format_order_status_string(order_id, email, mobile, shipping_info), ""
            else:
                return "Order not found.", "Could you please check the provided information and try again?"
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"
        
    @staticmethod
    def change_shipping_address(company_id: str, customer_id: int) -> str:
        """Check if the shipping address for the most recent order of a customer can be changed."""
        try:
            customer_df = df_orders[df_orders['customer_id'] == str(customer_id)]
            last_order_id = customer_df['order_id'].max()
            status = customer_df[customer_df['order_id'] == last_order_id]['status'].iloc[0]
            if status in ['Processing', 'Pending']:
                return f"You can change the shipping address for your most recent order with Order ID {last_order_id}."
            else:
                return f"You cannot change the shipping address for your most recent order with Order ID {last_order_id} as its status is {status}."
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e)
