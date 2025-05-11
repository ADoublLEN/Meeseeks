import time
import requests
from typing import List, Dict, Any

from source.model.base_model import BaseModel


class DemoApiModel(BaseModel):
    """
    This is a demo API model call which is used in our own scenario.
    Please implement your own model, either by using openai api or other methods.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip = kwargs.get("ip", "127.0.0.1")


    def generate(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        url = f"http://{self.ip}:8080"
        body = {
            "prompt": messages,
            "max_new_tokens": 2048,
            "multi_turn": True
        }
        retry = 0
        while retry < 5:
            try:
                response = requests.post(url, json=body)
                return response.json()["completions"][0]['text']
            except Exception as e:
                retry += 1
                print(f"Sending  request to {url} failed: {repr(e)}\n Retry [{retry}] in 10 secs...")
                time.sleep(10)
        raise Exception(f"Sending request to {url} failed after 5 retries.")