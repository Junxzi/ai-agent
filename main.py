import os
import yaml
from dotenv import load_dotenv

from bot import DataStore, JunBot


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    load_dotenv()
    config = load_config()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set")

    store = DataStore(config["database"]["path"])
    bot = JunBot(config, store)
    bot.run(token)


if __name__ == "__main__":
    main()
