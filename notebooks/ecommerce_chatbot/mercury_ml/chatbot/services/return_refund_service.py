import logging
from typing import Tuple, Optional
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.ecom_api import fetch_order_info, fetch_order_info_by_user
from mercury_ml.chatbot.utils.service_utils import (
    process_product_return,
    process_product_replacement,
)
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)


class ReturnRefundServiceFunctions:
    @staticmethod
    def replace_product(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        product_id: Optional[str] = None,
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

            if "order_status" in order_info:
                if order_info["order_status"].lower() == "fulfilled":
                    return process_product_replacement(
                        order_id, email, mobile, product_id, order_info
                    ), ""
                else:
                    return (
                        f"The product cannot be replaced as the order status is {order_info['order_status']}.",
                        "",
                    )
            else:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def return_product(
        company_id: str,
        order_id: Optional[int] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        product_id: Optional[str] = None,
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

            if "order_status" in order_info:
                if order_info["order_status"].lower() == "fulfilled":
                    return process_product_return(
                        company_id, order_id, email, mobile, product_id, order_info
                    ), ""
                else:
                    return (
                        f"The product cannot be returned as the order status is {order_info['order_status']}.",
                        "",
                    )
            else:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def initiate_return_or_refund(
        company_id: str, order_id: int, action: str
    ) -> Tuple[str, str]:
        """
        Initiates a return or refund process for a given order.
        Parameters:
        - order_id (int): The ID of the order.
        - action (str): The action to take, either 'return' or 'refund'.
        Returns:
        - Tuple[str, str]: A tuple containing a status message and a next step.
        """
        try:
            # Check if the order_id is valid
            if order_id not in df_orders["order_id"].values:
                return (
                    "Order not found.",
                    "Could you please check the provided information and try again?",
                )

            # Check if the action is valid
            if action not in ["return", "refund"]:
                return "Invalid action.", "Please specify either 'return' or 'refund'."

            # Update the database
            if action == "return":
                df_orders.loc[df_orders["order_id"] == order_id, "return_status"] = (
                    "Initiated"
                )
                status_message = (
                    f"The return process for Order ID {order_id} has been initiated."
                )
            else:  # action == 'refund'
                df_orders.loc[df_orders["order_id"] == order_id, "refund_status"] = (
                    "Initiated"
                )
                status_message = (
                    f"The refund process for Order ID {order_id} has been initiated."
                )

            next_step = "You will be contacted by our customer service team shortly."
            return status_message, next_step

        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_return_status(
        company_id: str,
        order_id: int = None,
        email: str = None,
        phone_number: str = None,
    ) -> Tuple[str, str]:
        """Get the return status of an order given its Order ID, email, or phone number.
        Returns: (status_message, next_step)
        """
        try:
            if order_id is not None:
                status = df_orders[df_orders["order_id"] == int(order_id)][
                    "return_status"
                ].iloc[0]
                return (
                    f"The return status of your order with Order ID {order_id} is {status}.",
                    "",
                )
            elif email is not None:
                status = df_orders[df_orders["email"] == email]["return_status"].iloc[0]
                return (
                    f"The return status of your order for email {email} is {status}.",
                    "",
                )
            elif phone_number is not None:
                status = df_orders[df_orders["phone_number"] == phone_number][
                    "return_status"
                ].iloc[0]
                return (
                    f"The return status of your order for phone number {phone_number} is {status}.",
                    "",
                )
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?",
                )
        except IndexError:
            return (
                "Order not found.",
                "Could you please check the provided information and try again?",
            )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_refund_status(
        company_id: str,
        order_id: int = None,
        email: str = None,
        phone_number: str = None,
    ) -> Tuple[str, str]:
        """Get the refund status of an order given its Order ID, email, or phone number.
        Returns: (status_message, next_step)
        """
        try:
            if order_id is not None:
                status = df_orders[df_orders["order_id"] == int(order_id)][
                    "refund_status"
                ].iloc[0]
                return (
                    f"The refund status of your order with Order ID {order_id} is {status}.",
                    "",
                )
            elif email is not None:
                status = df_orders[df_orders["email"] == email]["refund_status"].iloc[0]
                return (
                    f"The refund status of your order for email {email} is {status}.",
                    "",
                )
            elif phone_number is not None:
                status = df_orders[df_orders["phone_number"] == phone_number][
                    "refund_status"
                ].iloc[0]
                return (
                    f"The refund status of your order for phone number {phone_number} is {status}.",
                    "",
                )
            else:
                return (
                    "",
                    "Could you please provide the Order ID, email, or phone number?",
                )
        except IndexError:
            return (
                "Order not found.",
                "Could you please check the provided information and try again?",
            )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_return_policy(company_id: str, query: str) -> Tuple[str, str]:
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
                return (
                    "Unable to retrieve the return policy at the moment.",
                    "Please try again later.",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_refund_policy(company_id: str, query: str) -> Tuple[str, str]:
        """Get the refund policy of the company.
        Returns: (status_message, next_step)
        """
        try:
            # Retrieve the refund policy using chat engine
            rag = get_or_create_rag(company_id)
            response = rag.get_response(f"{query}")

            # Assuming the response contains the refund policy
            if response:
                return f"{response['output_text']}", ""
            else:
                return (
                    "Unable to retrieve the refund policy at the moment.",
                    "Please try again later.",
                )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"
