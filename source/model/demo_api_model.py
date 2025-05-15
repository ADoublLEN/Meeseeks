import asyncio
import time

import aiohttp
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


    async def generate(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        url = f"http://{self.ip}:8080"
        body = {
            "prompt": [messages],
            "max_new_tokens": 2048,
            "multi_turn": True
        }
        print(f"Sending request: {body}", flush=True)
        retry = 0
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_read=None, sock_connect=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while retry < 5:
                try:
                    async with session.post(url, json=body) as response:
                        result = await response.json()
                        return result["completions"][0]['text']
                except Exception as e:
                    retry += 1
                    print(f"Sending request to {url} failed: {repr(e)}\n Retry [{retry}] in 10 secs...", flush=True)
                    await asyncio.sleep(10)
        raise Exception(f"Sending request to {url} failed after 5 retries.")