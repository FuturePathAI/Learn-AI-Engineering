import logging
import copy
import logging
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

from mercury_ml.chatbot import config
from mercury_ml.chatbot.apis.shopagain import dump_gpt_api_call_details

# Initialize config
cfg = config.init_config()

# Configure logging
logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)
# Create a logger instance
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=cfg.openai_api.API_KEY)

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def chat_completion_request(messages,                            
                            temperature=0,
                            seed=123,
                            model=None,
                            top_p=1,
                            max_tokens=None,
                            functions=None,
                            function_call=None):
    if model is None:
        model = cfg.openai_api.CONVERSATION_MODEL

    # Log the request details
    logger.debug("Request to OpenAI API", extra={
        'method': 'POST',
        'path': 'https://api.openai.com/v1/chat/completions',
        'data': {
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'seed': seed,
            'top_p': top_p,
            'model': model,
            'functions': functions,
            'function_call': function_call
        }
    })
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            seed=seed,
            top_p=top_p,
            max_tokens=max_tokens,
            functions=functions,
            function_call=function_call
        )
        return completion
    except Exception as e:
        logging.error("Unable to generate ChatCompletion response")
        logging.error(f"Exception: {e}")
        return str(e)


def vision_completion_request(image_url, messages, model=None):
    if model is None:
        model = cfg.openai_api.VISION_MODEL

    messages_new = copy.deepcopy(messages)
    messages_new += [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What’s in this image?"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": image_url
            }
          }
        ]
      }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages_new,
            temperature=0,
            max_tokens=300
        )
        return response
    except Exception as e:
        logging.error("Unable to generate ChatCompletion response")
        logging.error(f"Exception: {e}")
        return str(e)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def embeddings_request(text, model=None):
    """
    Generate embeddings for the given text using the specified model.

    :param text: The text for which to generate embeddings.
    :param model: The model to use for generating embeddings. Default is "text-embedding-ada-002".
    :return: The embeddings as a list of floats.
    """
    if model is None:
        model = cfg.openai_api.EMBEDDING_MODEL
    
    try:
        response = client.embeddings.create(
            model=model,
            input=text,
            encoding_format="float"
        )        
        return response
    except Exception as e:
        logging.error("Unable to generate embeddings")
        logging.error(f"Exception: {e}")
        return str(e)