import os
import yaml
from dotenv import load_dotenv


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    load_dotenv()
    config = load_config()
    print("Config loaded:", config)
    print("Bot token prefix:", os.getenv("DISCORD_TOKEN", "<missing>")[:5])
    # Placeholder for bot start logic
    print("Bot starting... (not implemented)")


if __name__ == "__main__":
    main()
