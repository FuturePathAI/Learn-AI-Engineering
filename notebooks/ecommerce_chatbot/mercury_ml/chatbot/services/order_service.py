import logging
from typing import Tuple, Optional
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.ecom_api import (
    fetch_order_info,
    fetch_product_info,
    fetch_order_info_by_user,
)
from mercury_ml.chatbot.utils.service_utils import format_order_status_string
from mercury_ml.chatbot.utils.service_utils import call_human_agent
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)


class OrderServiceFunctions:
    @staticmethod
    def get_order_status(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
    ) -> Tuple[str, str]:
        try:
            if order_id is not None:
                order_info = fetch_order_info(company_id, str(order_id))
            elif email is not None:
                order_info = fetch_order_info_by_user(company_id, email=email)
            elif mobile is not None:
                order_info = fetch_order_info_by_user(company_id, mobile=mobile)
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?",
                )

            if order_info and "order_status" in order_info:
                return format_order_status_string(
                    order_id, email, mobile, order_info
                ), ""
            else:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def manage_order_change_request(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        ecom_chatbot=None,
    ) -> Tuple[str, str]:
        try:
            if order_id is not None:
                order_info = fetch_order_info(company_id, str(order_id))
            elif email is not None:
                order_info = fetch_order_info_by_user(company_id, email=email)
            elif mobile is not None:
                order_info = fetch_order_info_by_user(company_id, mobile=mobile)
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?"
                    + call_human_agent(ecom_chatbot),
                )

            if order_info and "order_status" in order_info:
                return format_order_status_string(
                    order_id, email, mobile, order_info
                ), "" + call_human_agent(ecom_chatbot)
            else:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?"
                    + call_human_agent(ecom_chatbot),
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(
                e
            ), "An error occurred. Could you please try again?" + call_human_agent(
                ecom_chatbot
            )

    @staticmethod
    def get_last_order_date(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
    ) -> Tuple[str, str]:
        try:
            if order_id is not None:
                order_info = fetch_order_info(company_id, str(order_id))
            elif email is not None:
                order_info = fetch_order_info_by_user(company_id, email=email)
            elif mobile is not None:
                order_info = fetch_order_info_by_user(company_id, mobile=mobile)
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?",
                )

            if "created_at" in order_info:
                return f"Your last order was placed on {order_info['created_at']}.", ""
            else:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_recent_order_products(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Confirm the products and quantities in the most recent order."""
        try:
            if order_id is not None:
                order_info = fetch_order_info(company_id, str(order_id))
            elif email is not None:
                order_info = fetch_order_info_by_user(company_id, email=email)
            elif mobile is not None:
                order_info = fetch_order_info_by_user(company_id, mobile=mobile)
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?",
                )

            if "external_product_ids" in order_info:
                last_order_id = order_info.get("external_order_id")
                external_product_ids = order_info.get("external_product_ids")
                logging.debug(f"last_order_id = {last_order_id}")
                logging.debug(f"external_product_ids = {external_product_ids}")

                # Fetch product information
                formatted_products = []
                for product_id in external_product_ids:
                    product_info = fetch_product_info(company_id, product_id)
                    if "name" in product_info:
                        formatted_products.append(
                            f"Product Name: {product_info['name']}"
                        )

                if formatted_products:
                    formatted_products_str = "\n".join(formatted_products)
                    return (
                        f"In your most recent order with Order ID {last_order_id}, you ordered the following products:\n{formatted_products_str}",
                        "",
                    )
                else:
                    return (
                        "No products found in the most recent order.",
                        "Could you please check the provided information and try again?",
                    )

            else:
                return (
                    "No products found in the most recent order.",
                    "Could you please check the provided information and try again?",
                )

        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"
