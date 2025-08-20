from schema import LlmRequestBody
import requests
from config import config

def prompt_llm(
    user_prompt: str,
    admin_prompt: str | None,
    llm_model_name: str,
) -> str | None:
    """
    Given prompts and model, request llm server and return response (text/media)
    """
    request_url = config.llm.get(
        "server_url", "http://localhost:8000/prompt"
        ) + config.llm.get(
            "endpoints", {}
            ).get("prompt", "")
    payload = LlmRequestBody(
        llm_model_name=llm_model_name,
        user_prompt=user_prompt,
        admin_prompt=admin_prompt,
        kwargs={}
    ).model_dump()
    print(f"Sending request to LLM with payload: {payload}")
    response = requests.post(request_url, json=payload)
    if response.status_code == 200:
        prompt_response = response.json().get("message")
        print(f"Received response from LLM: {prompt_response}")
        return prompt_response
    else:
        print("Error: Unable to get response from model")
        return None
    