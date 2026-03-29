"""Stub endpoints — to be expanded"""
from fastapi import APIRouter

# market.py
router_market = APIRouter()

@router_market.get("/macro")
async def get_macro():
    return {"status": "macro data endpoint"}

@router_market.get("/fear-greed")
async def fear_greed():
    from app.modules.data_collector import data_collector
    return await data_collector.get_fear_greed()

# journal.py
router_journal = APIRouter()

@router_journal.get("/trades")
async def get_trades():
    return {"trades": []}

@router_journal.post("/trades")
async def create_trade(data: dict):
    return {"status": "created", "id": "new_trade_id"}

# calendar.py
router_calendar = APIRouter()

@router_calendar.get("/events")
async def get_events():
    from app.modules.data_collector import data_collector
    events = await data_collector.get_economic_calendar()
    return {"events": events}

# watchlist.py
router_watchlist = APIRouter()

@router_watchlist.get("/")
async def get_watchlist():
    return {"items": []}

@router_watchlist.post("/add")
async def add_to_watchlist(data: dict):
    return {"status": "added"}

# strategies.py
router_strategies = APIRouter()

@router_strategies.get("/")
async def list_strategies():
    return {
        "strategies": [
            {"id": "ict_smc",   "name": "ICT / Smart Money Concepts", "type": "builtin", "active": True},
            {"id": "wyckoff",   "name": "Wyckoff Method",             "type": "builtin", "active": True},
            {"id": "elliott",   "name": "Elliott Wave",               "type": "builtin", "active": True},
            {"id": "vsa",       "name": "Volume Spread Analysis",     "type": "builtin", "active": True},
            {"id": "price_action","name": "Price Action Classic",     "type": "builtin", "active": True},
            {"id": "supply_demand","name": "Supply & Demand",         "type": "builtin", "active": True},
            {"id": "momentum",  "name": "Momentum",                  "type": "builtin", "active": True},
            {"id": "carry",     "name": "Carry Trade",               "type": "builtin", "active": True},
            {"id": "seasonal",  "name": "Seasonality",               "type": "builtin", "active": True},
            {"id": "tape",      "name": "Tape Reading",              "type": "builtin", "active": True},
            {"id": "dark_pool", "name": "Dark Pool Footprint",       "type": "builtin", "active": True},
            {"id": "iceberg",   "name": "Iceberg Detector",          "type": "builtin", "active": True},
            {"id": "gamma",     "name": "Options Gamma Squeeze",     "type": "builtin", "active": True},
            {"id": "ensemble",  "name": "Ensemble (All Strategies)", "type": "builtin", "active": True},
            {"id": "adaptive",  "name": "Adaptive (Regime-based)",   "type": "builtin", "active": True},
        ]
    }

# academy.py
router_academy = APIRouter()

@router_academy.get("/modules")
async def list_modules():
    return {
        "modules": [
            {"id": "01", "title": "How NEXUS Works",          "category": "system",    "duration": "15 min"},
            {"id": "02", "title": "ICT Concepts",             "category": "strategy",  "duration": "45 min"},
            {"id": "03", "title": "Wyckoff Method",           "category": "strategy",  "duration": "30 min"},
            {"id": "04", "title": "Risk Management",          "category": "risk",      "duration": "20 min"},
            {"id": "05", "title": "Psychology of Trading",    "category": "psychology","duration": "25 min"},
            {"id": "06", "title": "Reading Economic Calendar","category": "macro",     "duration": "15 min"},
            {"id": "07", "title": "Elliott Wave Basics",      "category": "strategy",  "duration": "35 min"},
            {"id": "08", "title": "Using the AI War Room",    "category": "system",    "duration": "20 min"},
            {"id": "09", "title": "Trade Journal Mastery",    "category": "system",    "duration": "15 min"},
            {"id": "10", "title": "Options Flow Basics",      "category": "data",      "duration": "25 min"},
        ]
    }

# notifications.py
router_notifications = APIRouter()

@router_notifications.post("/test")
async def test_notification(data: dict):
    from app.modules.notifications import notification_service
    result = await notification_service.broadcast(
        user_id="admin",
        message=f"🔔 NEXUS test notification",
        channels=data.get("channels", ["telegram"]),
    )
    return {"result": result}

# settings_api.py
router_settings = APIRouter()

@router_settings.get("/api-keys/list")
async def list_api_keys():
    from app.core.config import settings as s
    services = [
        {"id": "anthropic",    "name": "Claude API",      "configured": bool(s.ANTHROPIC_API_KEY),  "required": True},
        {"id": "gemini",       "name": "Google Gemini",   "configured": bool(s.GEMINI_API_KEY),     "required": False},
        {"id": "groq",         "name": "Groq",            "configured": bool(s.GROQ_API_KEY),       "required": False},
        {"id": "twelvedata",   "name": "TwelveData",      "configured": bool(s.TWELVE_DATA_KEY),    "required": False},
        {"id": "fred",         "name": "FRED (Macro)",    "configured": bool(s.FRED_API_KEY),       "required": False},
        {"id": "newsapi",      "name": "NewsAPI",         "configured": bool(s.NEWS_API_KEY),       "required": False},
        {"id": "binance",      "name": "Binance",         "configured": bool(s.BINANCE_API_KEY),    "required": False},
        {"id": "telegram",     "name": "Telegram Bot",    "configured": bool(s.TELEGRAM_BOT_TOKEN), "required": False},
        {"id": "elevenlabs",   "name": "ElevenLabs",      "configured": bool(s.ELEVENLABS_KEY),     "required": False},
        {"id": "deepgram",     "name": "Deepgram (Voice)","configured": bool(s.DEEPGRAM_KEY),       "required": False},
    ]
    return {"services": services}
