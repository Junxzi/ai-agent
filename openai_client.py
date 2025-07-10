import os
from typing import List, Dict
import yaml
import openai
from dotenv import load_dotenv


def load_config(path: str = "config.yaml") -> Dict:
    """Load YAML configuration from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class OpenAIClient:
    """Simple wrapper around the OpenAI ChatCompletion API."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        load_dotenv()
        config = load_config(config_path)
        self.model = config.get("openai", {}).get("model", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        openai.api_key = api_key

    def ask_chatgpt(self, prompt: str) -> str:
        """Send a prompt to ChatGPT and return the assistant's reply."""
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        return response["choices"][0]["message"]["content"]


# Convenience function
_client: OpenAIClient | None = None

def ask_chatgpt(prompt: str) -> str:
    """Module-level helper that uses a singleton OpenAIClient instance."""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client.ask_chatgpt(prompt)
