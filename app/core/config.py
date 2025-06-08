import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()


class Settings:
    POLYGON_RPC: str = os.getenv("POLYGON_RPC", "")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    PUBLIC_ADDRESS: str = Web3.to_checksum_address(
        os.getenv("PUBLIC_ADDRESS", ""))
    CONTRACT_ADDRESS: str = Web3.to_checksum_address(
        os.getenv("CONTRACT_ADDRESS", ""))
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    USE_LLM_ANALYSIS: bool = os.getenv(
        "USE_LLM_ANALYSIS", "true").lower() == "true"

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()
