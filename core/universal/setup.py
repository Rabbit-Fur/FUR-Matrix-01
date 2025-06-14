# core/universal/setup.py – FUR Codex Runtime Initializer
import os

def get_runtime_env():
    return {
        "python": os.getenv("CODEX_ENV_PYTHON_VERSION", "3.11.12"),
        "node": os.getenv("CODEX_ENV_NODE_VERSION", "20"),
        "rust": os.getenv("CODEX_ENV_RUST_VERSION", "1.87.0"),
        "go": os.getenv("CODEX_ENV_GO_VERSION", "1.23.8"),
        "swift": os.getenv("CODEX_ENV_SWIFT_VERSION", "6.1"),
        "discord_token": os.getenv("DISCORD_TOKEN"),
        "openai_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("BASE_URL", "https://fur-martix.up.railway.app/")
    }

def print_runtime_env():
    env = get_runtime_env()
    for key, val in env.items():
        print(f"{key.upper()}: {val if val else '🔴 NOT SET'}")

if __name__ == "__main__":
    print_runtime_env()
