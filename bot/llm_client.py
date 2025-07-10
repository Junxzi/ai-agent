from __future__ import annotations

from typing import Any, Dict, List
import openai


class LLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.model = config["openai"]["model"]
        self.temperature = config["openai"].get("temperature", 0.7)

    def chat(self, messages: List[Dict[str, str]], functions: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            functions=functions,
        )
        return response["choices"][0]
