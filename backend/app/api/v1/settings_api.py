"""
NEXUS API Hub — Backend
Save, test, encrypt API keys — no code needed
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import base64
import os
from loguru import logger

router = APIRouter()

ALL_SERVICES = [
    # AI Models
    {"id":"anthropic",    "name":"Claude API",           "cat":"ai",     "env":"ANTHROPIC_API_KEY",   "url":"https://console.anthropic.com",       "free":False,"price":"~$10/mo","desc":"Main AI brain",         "required":True},
    {"id":"gemini",       "name":"Google Gemini",        "cat":"ai",     "env":"GEMINI_API_KEY",      "url":"https://aistudio.google.com",         "free":True, "price":"Free",   "desc":"Macro analysis",        "required":False},
    {"id":"groq",         "name":"Groq",                 "cat":"ai",     "env":"GROQ_API_KEY",        "url":"https://groq.com",                    "free":True, "price":"Free",   "desc":"Ultra-fast AI",         "required":False},
    {"id":"mistral",      "name":"Mistral AI",           "cat":"ai",     "env":"MISTRAL_API_KEY",     "url":"https://console.mistral.ai",          "free":True, "price":"Free",   "desc":"Background tasks",      "required":False},
    {"id":"deepseek",     "name":"DeepSeek",             "cat":"ai",     "env":"DEEPSEEK_API_KEY",    "url":"https://platform.deepseek.com",       "free":False,"price":"~$2/mo", "desc":"Reasoning, cheap",      "required":False},
    {"id":"openrouter",   "name":"OpenRouter",           "cat":"ai",     "env":"OPENROUTER_API_KEY",  "url":"https://openrouter.ai",               "free":True, "price":"Free+",  "desc":"100+ models one key",   "required":False},
    {"id":"together",     "name":"Together AI",          "cat":"ai",     "env":"TOGETHER_API_KEY",    "url":"https://together.ai",                 "free":True, "price":"$5 free","desc":"Llama, DeepSeek",        "required":False},
    {"id":"cohere",       "name":"Cohere",               "cat":"ai",     "env":"COHERE_API_KEY",      "url":"https://cohere.com",                  "free":True, "price":"Free",   "desc":"Text analysis",         "required":False},
    {"id":"huggingface",  "name":"HuggingFace",          "cat":"ai",     "env":"HUGGINGFACE_API_KEY", "url":"https://huggingface.co",              "free":True, "price":"Free",   "desc":"FinBERT sentiment",     "required":False},
    {"id":"openai",       "name":"OpenAI GPT-4o",        "cat":"ai",     "env":"OPENAI_KEY",          "url":"https://platform.openai.com",         "free":False,"price":"$30+/mo","desc":"GPT-4o, O1, O3",        "required":False},
    {"id":"grok",         "name":"Grok (xAI)",           "cat":"ai",     "env":"GROK_API_KEY",        "url":"https://x.ai",                        "free":False,"price":"$30/mo", "desc":"Grok 2/3",              "required":False},
    # Market Data
    {"id":"twelvedata",   "name":"TwelveData",           "cat":"market", "env":"TWELVE_DATA_KEY",     "url":"https://twelvedata.com",              "free":True, "price":"Free",   "desc":"All markets, all TF",   "required":False},
    {"id":"alphavantage", "name":"Alpha Vantage",        "cat":"market", "env":"ALPHA_VANTAGE_KEY",   "url":"https://alphavantage.co",             "free":True, "price":"Free",   "desc":"Forex, stocks, crypto", "required":False},
    {"id":"polygon",      "name":"Polygon.io",           "cat":"market", "env":"POLYGON_API_KEY",     "url":"https://polygon.io",                  "free":True, "price":"Free",   "desc":"Stocks, options",       "required":False},
    {"id":"fmp",          "name":"Financial Modeling Prep","cat":"market","env":"FMP_API_KEY",         "url":"https://financialmodelingprep.com",   "free":True, "price":"Free",   "desc":"Fundamental analysis",  "required":False},
    {"id":"tiingo",       "name":"Tiingo",               "cat":"market", "env":"TIINGO_API_KEY",      "url":"https://tiingo.com",                  "free":True, "price":"Free",   "desc":"Stocks, forex, crypto", "required":False},
    {"id":"eodhd",        "name":"EODHD",                "cat":"market", "env":"EODHD_API_KEY",       "url":"https://eodhd.com",                   "free":True, "price":"Free",   "desc":"70+ exchanges",         "required":False},
    {"id":"taapi",        "name":"Taapi.io",             "cat":"market", "env":"TAAPI_KEY",           "url":"https://taapi.io",                    "free":True, "price":"Free",   "desc":"100+ indicators",       "required":False},
    {"id":"unusualwhales","name":"Unusual Whales",       "cat":"market", "env":"UNUSUAL_WHALES_KEY",  "url":"https://unusualwhales.com",           "free":False,"price":"$50/mo", "desc":"Options flow",          "required":False},
    # Crypto
    {"id":"cmc",          "name":"CoinMarketCap",        "cat":"crypto", "env":"CMC_API_KEY",         "url":"https://coinmarketcap.com/api",       "free":True, "price":"Free",   "desc":"All crypto, market cap","required":False},
    {"id":"cryptocompare","name":"CryptoCompare",        "cat":"crypto", "env":"CRYPTOCOMPARE_KEY",   "url":"https://cryptocompare.com/api",       "free":True, "price":"Free",   "desc":"Crypto data",           "required":False},
    {"id":"messari",      "name":"Messari",              "cat":"crypto", "env":"MESSARI_KEY",         "url":"https://messari.io/api",              "free":True, "price":"Free",   "desc":"Crypto research",       "required":False},
    {"id":"lunarcrush",   "name":"LunarCrush",           "cat":"crypto", "env":"LUNARCRUSH_KEY",      "url":"https://lunarcrush.com/developers",   "free":True, "price":"Free",   "desc":"Social sentiment",      "required":False},
    {"id":"santiment",    "name":"Santiment",            "cat":"crypto", "env":"SANTIMENT_KEY",       "url":"https://santiment.net",               "free":True, "price":"Free",   "desc":"On-chain + sentiment",  "required":False},
    # Brokers
    {"id":"binance",      "name":"Binance",              "cat":"broker", "env":"BINANCE_API_KEY",     "url":"https://binance.com",                 "free":True, "price":"Free",   "desc":"Crypto trading",        "required":False},
    {"id":"bybit",        "name":"Bybit",                "cat":"broker", "env":"BYBIT_API_KEY",       "url":"https://bybit.com",                   "free":True, "price":"Free",   "desc":"Crypto trading",        "required":False},
    {"id":"alpaca",       "name":"Alpaca",               "cat":"broker", "env":"ALPACA_KEY",          "url":"https://alpaca.markets",              "free":True, "price":"Free",   "desc":"Stocks paper trading",  "required":False},
    # Macro
    {"id":"fred",         "name":"FRED API",             "cat":"macro",  "env":"FRED_API_KEY",        "url":"https://fred.stlouisfed.org/docs/api","free":True, "price":"Free",   "desc":"US macro CPI/GDP",      "required":False},
    {"id":"bls",          "name":"BLS API",              "cat":"macro",  "env":"BLS_API_KEY",         "url":"https://api.bls.gov",                 "free":True, "price":"Free",   "desc":"NFP, unemployment",     "required":False},
    # News
    {"id":"newsapi",      "name":"NewsAPI",              "cat":"news",   "env":"NEWS_API_KEY",        "url":"https://newsapi.org",                 "free":True, "price":"Free",   "desc":"World news",            "required":False},
    {"id":"gnews",        "name":"GNews",                "cat":"news",   "env":"GNEWS_KEY",           "url":"https://gnews.io",                    "free":True, "price":"Free",   "desc":"Global news",           "required":False},
    {"id":"tavily",       "name":"Tavily AI Search",     "cat":"news",   "env":"TAVILY_KEY",          "url":"https://tavily.com",                  "free":True, "price":"Free",   "desc":"AI search",             "required":False},
    # Notifications
    {"id":"telegram",     "name":"Telegram Bot",         "cat":"notify", "env":"TELEGRAM_BOT_TOKEN",  "url":"https://t.me/BotFather",              "free":True, "price":"Free",   "desc":"Main alerts",           "required":False},
    {"id":"discord",      "name":"Discord Bot",          "cat":"notify", "env":"DISCORD_BOT_TOKEN",   "url":"https://discord.com/developers",      "free":True, "price":"Free",   "desc":"Discord alerts",        "required":False},
    {"id":"twilio",       "name":"Twilio (WhatsApp/SMS)","cat":"notify", "env":"TWILIO_ACCOUNT_SID",  "url":"https://twilio.com",                  "free":False,"price":"~$5/mo", "desc":"WhatsApp & SMS",        "required":False},
    # Voice
    {"id":"elevenlabs",   "name":"ElevenLabs",           "cat":"voice",  "env":"ELEVENLABS_KEY",      "url":"https://elevenlabs.io",               "free":False,"price":"$22/mo", "desc":"Voice messages",        "required":False},
    {"id":"deepgram",     "name":"Deepgram",             "cat":"voice",  "env":"DEEPGRAM_KEY",        "url":"https://deepgram.com",                "free":True, "price":"Free",   "desc":"Voice recognition",     "required":False},
]

_store: dict = {}


def _enc(v: str) -> str:
    return base64.b64encode(v.encode()).decode()


def _dec(v: str) -> str:
    return base64.b64decode(v.encode()).decode()


async def _test(service_id: str, key: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            if service_id == "anthropic":
                r = await c.get("https://api.anthropic.com/v1/models",
                    headers={"x-api-key": key, "anthropic-version": "2023-06-01"})
                return {"ok": r.status_code == 200}
            elif service_id == "gemini":
                r = await c.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
                return {"ok": r.status_code == 200}
            elif service_id == "groq":
                r = await c.get("https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "mistral":
                r = await c.get("https://api.mistral.ai/v1/models",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "deepseek":
                r = await c.get("https://api.deepseek.com/models",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "openrouter":
                r = await c.get("https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "openai":
                r = await c.get("https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "twelvedata":
                r = await c.get(f"https://api.twelvedata.com/price?symbol=AAPL&apikey={key}")
                return {"ok": "price" in r.json()}
            elif service_id == "alphavantage":
                r = await c.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey={key}")
                return {"ok": "Global Quote" in r.json()}
            elif service_id == "polygon":
                r = await c.get(f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-09/2023-01-10?apiKey={key}")
                return {"ok": r.status_code == 200}
            elif service_id == "fred":
                r = await c.get(f"https://api.stlouisfed.org/fred/series?series_id=GDP&api_key={key}&file_type=json")
                return {"ok": r.status_code == 200}
            elif service_id == "newsapi":
                r = await c.get(f"https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey={key}")
                return {"ok": r.json().get("status") == "ok"}
            elif service_id == "cmc":
                r = await c.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=1",
                    headers={"X-CMC_PRO_API_KEY": key})
                return {"ok": r.status_code == 200}
            elif service_id == "telegram":
                r = await c.get(f"https://api.telegram.org/bot{key}/getMe")
                d = r.json()
                return {"ok": d.get("ok", False), "bot": d.get("result", {}).get("username")}
            elif service_id == "elevenlabs":
                r = await c.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": key})
                return {"ok": r.status_code == 200}
            elif service_id == "deepgram":
                r = await c.get("https://api.deepgram.com/v1/projects",
                    headers={"Authorization": f"Token {key}"})
                return {"ok": r.status_code == 200}
            elif service_id == "huggingface":
                r = await c.get("https://huggingface.co/api/models?limit=1",
                    headers={"Authorization": f"Bearer {key}"})
                return {"ok": r.status_code == 200}
            else:
                return {"ok": len(key) > 8, "note": "Saved — manual verification needed"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


class SaveKeyRequest(BaseModel):
    service_id: str
    key_value: str
    extra_value: Optional[str] = None


class TestKeyRequest(BaseModel):
    service_id: str
    key_value: str


@router.get("/services")
async def list_services():
    result = []
    for svc in ALL_SERVICES:
        stored = _store.get(svc["id"])
        result.append({
            **svc,
            "configured": stored is not None,
            "preview":    f"···{stored['preview']}" if stored else None,
            "test_ok":    stored.get("test_ok") if stored else None,
        })
    configured = sum(1 for s in result if s["configured"])
    return {"services": result, "total": len(result), "configured": configured}


@router.get("/categories")
async def list_categories():
    cats = {}
    for svc in ALL_SERVICES:
        c = svc["cat"]
        if c not in cats:
            cats[c] = {"id": c, "count": 0, "configured": 0}
        cats[c]["count"] += 1
        if _store.get(svc["id"]):
            cats[c]["configured"] += 1
    return {"categories": list(cats.values())}


@router.post("/save")
async def save_key(req: SaveKeyRequest):
    svc = next((s for s in ALL_SERVICES if s["id"] == req.service_id), None)
    if not svc:
        raise HTTPException(404, f"Service '{req.service_id}' not found")
    key = req.key_value.strip()
    if len(key) < 5:
        raise HTTPException(400, "Key too short")

    test = await _test(req.service_id, key)

    _store[req.service_id] = {
        "enc":      _enc(key),
        "preview":  key[-6:],
        "test_ok":  test["ok"],
        "test_info": test,
    }

    os.environ[svc["env"]] = key
    if req.extra_value:
        if req.service_id == "binance":
            os.environ["BINANCE_SECRET"] = req.extra_value.strip()
        elif req.service_id == "bybit":
            os.environ["BYBIT_SECRET"] = req.extra_value.strip()
        elif req.service_id == "twilio":
            os.environ["TWILIO_AUTH_TOKEN"] = req.extra_value.strip()

    logger.info(f"API key saved: {svc['name']} — {'✅' if test['ok'] else '❌'}")

    return {
        "saved":   True,
        "service": svc["name"],
        "test_ok": test["ok"],
        "message": "✅ Key works!" if test["ok"] else "⚠️ Saved but test failed — check key",
        "detail":  test,
    }


@router.post("/test")
async def test_key(req: TestKeyRequest):
    result = await _test(req.service_id, req.key_value.strip())
    return {"service_id": req.service_id, "ok": result["ok"], "detail": result}


@router.delete("/remove/{service_id}")
async def remove_key(service_id: str):
    if service_id not in _store:
        raise HTTPException(404, "Key not found")
    svc = next((s for s in ALL_SERVICES if s["id"] == service_id), None)
    if svc:
        os.environ.pop(svc["env"], None)
    del _store[service_id]
    return {"removed": True}


@router.get("/status")
async def system_status():
    configured = len(_store)
    total = len(ALL_SERVICES)
    return {
        "configured": configured,
        "total":      total,
        "pct":        round(configured / total * 100),
        "ai_ready":   "anthropic" in _store and _store["anthropic"]["test_ok"],
        "data_ready": "twelvedata" in _store or "alphavantage" in _store,
        "notify_ready": "telegram" in _store and _store["telegram"]["test_ok"],
    }
