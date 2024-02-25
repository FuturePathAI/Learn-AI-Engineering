"""
This is a skeleton for a FastAPI application that interacts with an LLM which you can use as a starting point.
You need to host a FastAPI server to interact with the LLM. This server will receive requests from the client and send them to the LLM.
The server must definitely have the following endpoints:
- /api/generate: This endpoint will receive the request from the client, process it and send it to the LLM.
- /status: This endpoint will be used to check the status of the server. And must return a 200 status code if the server is running and a {"status": "ok"} message.

We also recommend you add the following endpoints to the server to make it easier to "chain" and scale your LLM apps:
- /api/embed: This endpoint will receive a text and return its embedding.
- /api/similarity: This endpoint will receive a text and return their nearest neighbors from an index.
- /api/rerank: This endpoint will receive a list of texts, a query and return a ranked list of the texts.
- /api/summarize: This endpoint will receive a text and return a summary of the text.
- /api/translate: This endpoint will receive a text and return a translation of the text.
"""

from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel


class LLM(BaseModel):
    """
    You can specify the LLM parameters to use in this model
    """
    llm: Dict

class UserRequest(BaseModel):
    """
    This model represents the request that the server will receive from the client. 
    In the Augment Assignment, the client will send a request with the ranked results 
    """
    user_request: str
    prompt: str
    context: List[str]

app = FastAPI()

def llm_logic(LLMRequest) -> str:
    """
    Here you would add your logic to process the request and interact with the LLM
    For demonstration, we'll just echo the received request
    """
    ...

@app.post("/generate")
async def process_llm(request: UserRequest) -> Dict[Any, Any]:
    llm_response = llm_logic(request)
    response = {
        "llm": request.llm,
        "user_request": request.user_request,
        "prompt": request.prompt,
        "context": request.context,
        "llm_response": "Your LLM logic would determine this response."
    }
    return response
