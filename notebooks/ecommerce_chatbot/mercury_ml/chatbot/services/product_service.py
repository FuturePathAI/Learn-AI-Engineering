import logging
from typing import Tuple
from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.ecom_api import fetch_product_info
from mercury_ml.chatbot.rag.get_rag import get_or_create_rag

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)


class ProductServiceFunctions:
    @staticmethod
    def get_product_info(company_id: str, product_id: str = None) -> Tuple[str, str]:
        try:
            if product_id is None:
                return "", "Could you please provide the Product ID?"

            product_info = fetch_product_info(company_id, product_id)

            if "error" in product_info:
                return product_info[
                    "error"
                ], "An error occurred. Could you please try again?"

            if not product_info:
                return (
                    f"No information found for Product ID {product_id}.",
                    "Would you like to search for another product?",
                )

            return (
                f"Details for Product ID {product_id}: Name - {product_info['name']}, Price - {product_info['price']}",
                "",
            )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_product_variants(
        company_id: str, product_id: str = None
    ) -> Tuple[str, str]:
        try:
            if product_id is None:
                return "", "Could you please provide the Product ID?"

            product_info = fetch_product_info(company_id, product_id)

            if "error" in product_info:
                return product_info[
                    "error"
                ], "An error occurred. Could you please try again?"

            variants = product_info.get("variants", [])

            if len(variants) < 2:
                return f"No variants found for Product ID {product_id}.", ""

            variant_details = [
                f"ID: {variant['sku']}, Title: {variant['title']}, Price: {variant['price']}"
                for variant in variants
            ]

            return "Other variants available for Product ID " + str(
                product_id
            ) + ":\n" + "\n".join(variant_details), ""
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"

    @staticmethod
    def get_product_vendor(company_id: str, product_id: str = None) -> Tuple[str, str]:
        try:
            if product_id is None:
                return "", "Could you please provide the Product ID?"

            product_info = fetch_product_info(company_id, product_id)

            if "error" in product_info:
                return product_info[
                    "error"
                ], "An error occurred. Could you please try again?"

            if "vendor" not in product_info:
                return f"The product with Product ID {product_id} is not available.", ""

            return (
                f"The product with Product ID {product_id} is available from Vendor {product_info['vendor']}.",
                "",
            )
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            return str(e), "An error occurred. Could you please try again?"
