import logging
from typing import Dict, Any, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.fake_responses import (
    fake_order_info_response,
    fake_product_info_response,
)

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_product_info(
    company_id: str, product_id: Optional[str] = None
) -> Dict[str, Any]:
    try:
        data = {
            "company_id": company_id,
            "function_name": "get_product_info",
            "kwargs": {"product_id": product_id},
        }

        logging.debug(f"data: {data}")
        return fake_product_info_response
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {"error": str(e)}


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_order_info(company_id: str, order_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        data = {
            "company_id": company_id,
            "function_name": "get_order_info",
            "kwargs": {"order_id": order_id},
        }

        logging.debug(f"data: {data}")
        return fake_order_info_response
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {"error": str(e)}


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_order_info_by_user(
    company_id: str, email: Optional[str] = None, mobile: Optional[str] = None
) -> Dict[str, Any]:
    try:
        kwargs = {}
        if email is not None:
            kwargs["email"] = email
        elif mobile is not None:
            kwargs["mobile"] = mobile
        else:
            logging.error("Either email or mobile must be provided")
            return {"error": "Either email or mobile must be provided"}

        data = {
            "company_id": company_id,
            "function_name": "get_last_order_for_user",
            "kwargs": kwargs,
        }

        logging.debug(f"data: {data}")
        return fake_order_info_response
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {"error": str(e)}
