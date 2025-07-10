import os
import logging
from logging.handlers import RotatingFileHandler

import yaml
from dotenv import load_dotenv

from bot import DataStore, JunBot


def setup_logging(config: dict) -> None:
    """Configure root logger for both file and console output."""
    level_str = str(config.get("logging", {}).get("level", "INFO")).upper()
    log_file = config.get("logging", {}).get("file", "junbot.log")

    level = getattr(logging, level_str, logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    load_dotenv()
    config = load_config()
    setup_logging(config)
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set")

    store = DataStore(config["database"]["path"])
    bot = JunBot(config, store)
    bot.run(token)


if __name__ == "__main__":
    main()
