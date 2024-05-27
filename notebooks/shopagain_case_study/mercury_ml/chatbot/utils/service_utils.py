import logging
from typing import Tuple, Dict, Any, Optional, Union
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.openai import chat_completion_request

# initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)

def format_order_status_string(order_id: Optional[int], email: Optional[str], mobile: Optional[str], order_info: dict) -> str:
    status_str = ""
    if order_id is not None:
        status_str = f"The status of your order with Order ID {order_id} is {order_info['order_status']}."
    elif email is not None:
        status_str = f"The status of your order for email {email} is {order_info['order_status']}."
    elif mobile is not None:
        status_str = f"The status of your order for phone number {mobile} is {order_info['order_status']}."

    # Check if the order status is "placed" and needs_processing is True
    if order_info['order_status'].lower() == 'placed' and order_info.get('original_doc', {}).get('needs_processing', False):
        status_str += " The order is currently being processed by our team."
    
    if 'order_status_url' in order_info and order_info['order_status_url'] is not None:
        status_str += f"\nYou can check the details here: {order_info['order_status_url']}"
    
    if 'tracking_urls' in order_info and order_info['tracking_urls']:
        tracking_links = "\n".join(order_info['tracking_urls'])
        status_str += f"\nTracking information is available at:\n{tracking_links}"

    return status_str

def process_product_replacement(order_id: Optional[int] = None, email: Optional[str] = None, mobile: Optional[str] = None, product_id: Optional[str] = None, order_info: dict = None) -> str:
    identifier_info = []
    
    if order_id is not None:
        identifier_info.append(f"Order ID: {order_id}")
    
    if email is not None:
        identifier_info.append(f"Email: {email}")
        
    if mobile is not None:
        identifier_info.append(f"Mobile: {mobile}")

    identifier_string = " or ".join(identifier_info)

    product_info = f"Product {product_id}" if product_id is not None else "The product"
    
    if identifier_info:
        return f"{product_info} in order with {identifier_string} is eligible for replacement. Our team will contact you."
    else:
        return "Could you please provide either an Order ID, Email, Mobile, or Product ID for replacement. Our team will contact you."

def process_product_return(order_id: Optional[int] = None, email: Optional[str] = None, mobile: Optional[str] = None, product_id: Optional[str] = None, order_info: dict = None) -> str:
    identifier_info = []
    
    if order_id is not None:
        identifier_info.append(f"Order ID: {order_id}")
    
    if email is not None:
        identifier_info.append(f"Email: {email}")
        
    if mobile is not None:
        identifier_info.append(f"Mobile: {mobile}")

    identifier_string = " or ".join(identifier_info)

    product_info = f"Product {product_id}" if product_id is not None else "The product"
    
    if identifier_info:
        return f"{product_info} in order with {identifier_string} is eligible for return. Our team will contact you."
    else:
        return "Could you please provide either an Order ID, Email, Mobile, or Product ID for return. Our team will contact you."
        
def get_static_methods(cls):
    base_attrs = set(dir(type('dummy', (object,), {})))
    return [method for method in dir(cls) if callable(getattr(cls, method)) and not any(getattr(getattr(cls, method), key, None) for key in ["__self__", "__func__"]) and method not in base_attrs]

def beautify_service_response(input_text: Union[str, Tuple[str, ...]], messages: list, ResponseBeautifierBasePrompt: str) -> str:
    logging.debug(f"Received input_text: {input_text}")
    
    # Convert tuple to string if needed
    if isinstance(input_text, tuple):
        input_text = ' '.join(input_text)    
        
    messages.append({"role": "system", "content": ResponseBeautifierBasePrompt})
    messages.append({"role": "function", "content": input_text})
    response = chat_completion_request(messages)
    print("response.json() = ",response.json())
    beautified_text = response.json()['choices'][0]['message']['content']
    
    logging.debug(f"Generated beautified_text: {beautified_text}")    
    return beautified_text

def call_human_agent(ecom_chatbot):
    if ecom_chatbot:
        ecom_chatbot.call_human = True
        
    logging.debug(f"Invoked call_human_agent()...")
    return "\nAssigning to a human agent now."
    