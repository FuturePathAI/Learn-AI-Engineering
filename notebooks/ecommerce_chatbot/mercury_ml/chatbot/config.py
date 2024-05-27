import logging
import os
from pathlib import Path

from easydict import EasyDict as edict
from dotenv import load_dotenv

load_dotenv()


def init_config():
    cfg = edict()

    cfg.LOGGING_LEVEL = logging.DEBUG

    # openai_api
    cfg.openai_api = edict()
    cfg.openai_api.CONVERSATION_MODEL = "gpt-3.5-turbo-0613"
    cfg.openai_api.EMBEDDING_MODEL = "text-embedding-ada-002"
    cfg.openai_api.VISION_MODEL = "gpt-4-vision-preview"
    cfg.openai_api.URL = "https://api.openai.com/v1/chat/completions"
    cfg.openai_api.API_KEY = os.getenv("OPENAI_API_KEY")
    cfg.openai_api.HEADERS = {
        "Authorization": "Bearer " + cfg.openai_api.API_KEY,
        "Content-Type": "application/json",
    }
    # prompts
    cfg.prompts = edict()
    cfg.prompts.PATH_SELECTOR_PROMPT = (
        "mercury_ml/chatbot/prompts/service_selector_prompts.yaml"
    )
    cfg.prompts.PATH_SERVICE_PROMPT = "mercury_ml/chatbot/prompts/service_prompts.yaml"
    cfg.prompts.PATH_PERSONA_PROMPT = "mercury_ml/chatbot/prompts/persona_prompts.yaml"

    # langchain-rag
    cfg.rag = edict()

    cfg.rag.KNOWLEDGE_BASE_DIR = str((Path(__file__) / "../data/").resolve())
    cfg.rag.PERSIST_DIR = "/home/ubuntu/data/chatbot/vectorstore"
    if os.environ.get("RAG_PERSIST_DIR"):
        cfg.rag.PERSIST_DIR = os.environ["RAG_PERSIST_DIR"]

    cfg.rag.CONVERSATION_MODEL = "gpt-3.5-turbo"
    cfg.rag.EMBEDDING_MODEL = "text-embedding-ada-002"
    cfg.rag.CHUNK_SIZE = 1000
    cfg.rag.CHUNK_OVERLAP = 50
    cfg.rag.OPENAI_TEMPERATURE = 0.2

    # marvin
    cfg.marvin = edict()
    cfg.marvin.PRIMARY_MODEL = "gpt-3.5-turbo-0613"
    cfg.marvin.SECONDARY_MODEL = "gpt-4"
    cfg.marvin.LLM_TEMPERATURE = 0.2
    cfg.marvin.LLM_MAX_TOKENS = 1500
    cfg.marvin.PRODUCT_TYPES: dict = {
        "6b0173e7-bd13-4046-b8fa-d5d39240950e": "personalized jewelry",  # inaya
        "2c7aaa94-4cd2-4a55-a220-6dd150bcc910": "personalized jewelry",  # inaya shopify,
        "8f6a44b2-4fa4-4ae2-86f7-9ef90a97021d": "sticker store",  # stickerlane
    }

    # store specific information
    cfg.store_info = edict()
    cfg.store_info.EMAIL: dict = {
        "6b0173e7-bd13-4046-b8fa-d5d39240950e": "support@inayaaccessories.com",  # inaya
        "2c7aaa94-4cd2-4a55-a220-6dd150bcc910": "support@inayaaccessories.com",  # inaya shopify,
    }
    cfg.store_info.PHONE: dict = {
        "6b0173e7-bd13-4046-b8fa-d5d39240950e": "WhatsApp +918355940180 (calling not available)",  # inaya
        "2c7aaa94-4cd2-4a55-a220-6dd150bcc910": "WhatsApp +918355940180 (calling not available)",  # inaya shopify,
    }
    return cfg
