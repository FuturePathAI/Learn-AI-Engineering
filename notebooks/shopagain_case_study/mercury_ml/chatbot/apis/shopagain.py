import json
import logging
import requests
from typing import Dict, Any, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
from mercury_ml.chatbot import config

# Initialize config
cfg = config.init_config()

logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format='%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s',
)

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_product_info(company_id: str, product_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        data = {'company_id': company_id,
                'function_name': 'get_product_info',
                'kwargs': {'product_id': product_id}
               }

        logging.debug(f"data: {data}")
        r = requests.post(url=cfg.shopagain_api.URL, headers=cfg.shopagain_api.HEADERS, json=data)
        
        if r.status_code == 200:
            return json.loads(r.text)['data']
        else:
            logging.warning(f"Received non-200 status code: {r.status_code}")
            return {}
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {'error': str(e)}

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_order_info(company_id: str, order_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        data = {'company_id': company_id,
                'function_name': 'get_order_info',
                'kwargs': {'order_id': order_id}
               }

        logging.debug(f"data: {data}")
        r = requests.post(url=cfg.shopagain_api.URL, headers=cfg.shopagain_api.HEADERS, json=data)
        
        if r.status_code == 200:
            return json.loads(r.text)['data']
        else:
            logging.warning(f"Received non-200 status code: {r.status_code}")
            return {}
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {'error': str(e)}

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def fetch_order_info_by_user(company_id: str, email: Optional[str] = None, mobile: Optional[str] = None) -> Dict[str, Any]:
    try:
        kwargs = {}
        if email is not None:
            kwargs['email'] = email
        elif mobile is not None:
            kwargs['mobile'] = mobile
        else:
            logging.error("Either email or mobile must be provided")
            return {'error': 'Either email or mobile must be provided'}
        
        data = {
            'company_id': company_id,
            'function_name': 'get_last_order_for_user',
            'kwargs': kwargs
        }

        logging.debug(f"data: {data}")
        r = requests.post(url=cfg.shopagain_api.URL, headers=cfg.shopagain_api.HEADERS, json=data)
        
        if r.status_code == 200:
            return json.loads(r.text)['data']
        else:
            logging.warning(f"Received non-200 status code: {r.status_code}")
            return {}
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {'error': str(e)}


def dump_gpt_api_call_details(company_id: str, request_data: dict, response_data: dict, response_status_code: int, model: str, provider: str):
    """dump openai or azure api call details to database for outage detection and analytics

    Args:
        company_id (str):
        request_data (dict):
        response_data (dict):
        response_status_code (int):
        model (str): GPT3 or GPT4
        provider (str): azure or openai

    Returns:
        _type_: _description_
    """
    try:
        data = {
            'company_id': company_id,
            'request_data': request_data,
            'response_data': response_data,
            'response_status_code': response_status_code,
            'model': model,
            'provider': provider,
            'function_name': 'dump_gpt_api_call_details',
        }

        logging.debug(f"dump_gpt_api_call_details data: {data}")
        r = requests.post(url=cfg.shopagain_api.URL, headers=cfg.shopagain_api.HEADERS, json=data)
        
        if r.status_code == 200:
            return json.loads(r.text)['data']
        else:
            logging.warning(f"Received non-200 status code: {r.status_code} {r.text}")
            return {}
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return {'error': str(e)}
