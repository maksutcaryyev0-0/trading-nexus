from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-in-production"
    MASTER_PASSWORD: str = "change-this"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    TIMEZONE: str = "Europe/Moscow"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexus.db"
    POSTGRES_PASSWORD: str = "nexus"
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "nexus_knowledge"
    JWT_SECRET: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: str = "change-this-32-char-encrypt-key!"
    CORS_ORIGINS: List[str] = ["http://localhost:3000","https://*.vercel.app"]
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    OPENAI_KEY: Optional[str] = None
    ZHIPU_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_KEY: Optional[str] = None
    TWELVE_DATA_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    FMP_API_KEY: Optional[str] = None
    TIINGO_API_KEY: Optional[str] = None
    NASDAQ_DATA_KEY: Optional[str] = None
    EODHD_API_KEY: Optional[str] = None
    TAAPI_KEY: Optional[str] = None
    CMC_API_KEY: Optional[str] = None
    CRYPTOCOMPARE_KEY: Optional[str] = None
    MESSARI_KEY: Optional[str] = None
    LUNARCRUSH_KEY: Optional[str] = None
    SANTIMENT_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET: Optional[str] = None
    BINANCE_TESTNET: bool = True
    BYBIT_API_KEY: Optional[str] = None
    BYBIT_SECRET: Optional[str] = None
    BYBIT_TESTNET: bool = True
    FRED_API_KEY: Optional[str] = None
    BLS_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    GNEWS_KEY: Optional[str] = None
    TAVILY_KEY: Optional[str] = None
    MT5_LOGIN: Optional[str] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None
    ALPACA_KEY: Optional[str] = None
    ALPACA_SECRET: Optional[str] = None
    ALPACA_PAPER: bool = True
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ADMIN_ID: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE: Optional[str] = None
    ADMIN_PHONE: Optional[str] = None
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    DISCORD_BOT_TOKEN: Optional[str] = None
    DISCORD_CHANNEL_ID: Optional[str] = None
    ELEVENLABS_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None
    DEEPGRAM_KEY: Optional[str] = None
    NOTION_TOKEN: Optional[str] = None
    TRADINGVIEW_WEBHOOK_SECRET: Optional[str] = None
    BACKUP_S3_BUCKET: Optional[str] = None
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    AWS_REGION: str = "eu-central-1"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def available_ai_models(self) -> dict:
        models = {}
        if self.ANTHROPIC_API_KEY: models["claude"] = "claude-sonnet-4-6"
        if self.GEMINI_API_KEY: models["gemini"] = "gemini-1.5-pro"
        if self.GROQ_API_KEY: models["groq"] = "llama-3.1-70b-versatile"
        if self.DEEPSEEK_API_KEY: models["deepseek"] = "deepseek-chat"
        if self.MISTRAL_API_KEY: models["mistral"] = "mistral-large-latest"
        return models


settings = Settings()
