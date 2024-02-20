import os
import warnings
warnings.filterwarnings('ignore')

import logging
import openai
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt


# Configure logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY_FUTUREPATH_ML')
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=openai.api_key)

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def chat_completion_request(messages,                            
                            temperature=0.5,
                            seed=123,
                            model=None,
                            top_p=1,
                            max_tokens=None,
                            response_format=None,
                            functions=None,
                            function_call=None):
    if model is None:
        model = 'gpt-3.5-turbo-0125'
    
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
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Exception: {e}")
        return str(e)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def chat_completion_request_tokens(messages,                            
                            temperature=0,
                            seed=123,
                            model=None,
                            top_p=1,
                            max_tokens=None,
                            functions=None,
                            function_call=None):
    if model is None:
        model = 'gpt-3.5-turbo-0125'

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

        # Extract token usage from the completion response
        total_tokens = completion.usage.total_tokens
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens
        return completion, (total_tokens, input_tokens, output_tokens)
    except Exception as e:
        logging.exception("Unable to generate ChatCompletion response")
        logging.error(f"Exception: {e}")
        return None, (0, 0, 0)