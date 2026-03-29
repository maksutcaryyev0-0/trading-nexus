from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.modules.ai_war_room import ai_war_room
from app.modules.data_collector import data_collector
from app.modules.risk_engine import risk_engine

router = APIRouter()


class AnalysisRequest(BaseModel):
    symbol: str
    lang: str = "en"
    timezone: str = "UTC"
    timeframe: str = "H1"
    include_futures: bool = True
    include_options: bool = True


class QuickAnalysisRequest(BaseModel):
    symbol: str
    question: str
    lang: str = "en"


@router.post("/full")
async def full_analysis(req: AnalysisRequest):
    """
    Full institutional analysis — all 20+ sections
    Supports: XAUUSD, BTCUSDT, EURUSD, SPX500, and any symbol
    """
    symbol = req.symbol.upper()

    # Collect all available data
    price_data = await data_collector.get_price(symbol)
    ohlcv = await data_collector.get_ohlcv(symbol, req.timeframe, limit=200)
    news = await data_collector.get_news(symbol, req.lang)
    fg = await data_collector.get_fear_greed()

    # Build market data context
    market_data = {
        "symbol": symbol,
        "price": price_data.get("price"),
        "ohlcv_count": len(ohlcv),
        "recent_ohlcv": ohlcv[-20:] if ohlcv else [],
        "news_count": len(news),
        "recent_news": news[:5],
        "fear_greed": fg,
        "timeframe": req.timeframe,
        "quality": price_data.get("quality", "OBSERVED"),
        "include_futures": req.include_futures,
        "include_options": req.include_options,
    }

    # Run AI War Room
    result = await ai_war_room.full_analysis(
        symbol=symbol,
        market_data=market_data,
        user_id="current_user",
        lang=req.lang,
        timezone=req.timezone,
    )

    return result


@router.post("/quick")
async def quick_analysis(req: QuickAnalysisRequest):
    """Quick AI answer for chat panel"""
    answer = await ai_war_room.quick_analysis(
        symbol=req.symbol.upper(),
        question=req.question,
        lang=req.lang,
    )
    return {"answer": answer, "symbol": req.symbol.upper()}


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Live price with source and quality"""
    data = await data_collector.get_price(symbol.upper())
    return data


@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 200,
):
    """OHLCV candle data for charts"""
    candles = await data_collector.get_ohlcv(
        symbol.upper(), timeframe, limit
    )
    return {"symbol": symbol.upper(), "timeframe": timeframe, "candles": candles}


@router.get("/sessions")
async def get_sessions(timezone: str = "UTC"):
    """Trading sessions with times in user timezone"""
    import pytz
    from datetime import datetime

    sessions = {
        "asian":  {"open": "00:00", "close": "09:00", "tz": "Asia/Tokyo",   "color": "#3B8BD4"},
        "london": {"open": "08:00", "close": "17:00", "tz": "Europe/London", "color": "#1D9E75"},
        "new_york":{"open": "13:00","close": "22:00", "tz": "America/New_York","color": "#D85A30"},
        "overlap": {"open": "13:00","close": "17:00", "tz": "UTC",           "color": "#7F77DD"},
    }

    try:
        user_tz = pytz.timezone(timezone)
        utc_now = datetime.now(pytz.UTC)
        user_now = utc_now.astimezone(user_tz)

        result = {}
        for name, s in sessions.items():
            result[name] = {
                **s,
                "user_timezone": timezone,
                "is_open": False,
                "note": f"Times in {s['tz']}",
            }
        return {
            "sessions": result,
            "server_time_utc": utc_now.isoformat(),
            "user_time": user_now.isoformat(),
            "user_timezone": timezone,
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/regimes")
async def get_market_regimes():
    """Available market regime types"""
    return {
        "regimes": [
            {"id": "trend",        "label": "Trend",         "color": "#1D9E75"},
            {"id": "range",        "label": "Range",         "color": "#378ADD"},
            {"id": "expansion",    "label": "Expansion",     "color": "#D85A30"},
            {"id": "compression",  "label": "Compression",   "color": "#7F77DD"},
            {"id": "event",        "label": "Event Day",     "color": "#E24B4A"},
            {"id": "low_conv",     "label": "Low Conviction","color": "#888780"},
            {"id": "high_opp",     "label": "High Opportunity","color": "#EF9F27"},
        ]
    }


@router.get("/timeframes")
async def get_timeframes():
    """All supported timeframes"""
    return {
        "timeframes": [
            {"id": "M1",  "label": "1 min",   "seconds": 60},
            {"id": "M2",  "label": "2 min",   "seconds": 120},
            {"id": "M3",  "label": "3 min",   "seconds": 180},
            {"id": "M5",  "label": "5 min",   "seconds": 300},
            {"id": "M10", "label": "10 min",  "seconds": 600},
            {"id": "M15", "label": "15 min",  "seconds": 900},
            {"id": "M20", "label": "20 min",  "seconds": 1200},
            {"id": "M30", "label": "30 min",  "seconds": 1800},
            {"id": "H1",  "label": "1 hour",  "seconds": 3600},
            {"id": "H2",  "label": "2 hours", "seconds": 7200},
            {"id": "H3",  "label": "3 hours", "seconds": 10800},
            {"id": "H4",  "label": "4 hours", "seconds": 14400},
            {"id": "H6",  "label": "6 hours", "seconds": 21600},
            {"id": "H8",  "label": "8 hours", "seconds": 28800},
            {"id": "H12", "label": "12 hours","seconds": 43200},
            {"id": "D1",  "label": "Daily",   "seconds": 86400},
            {"id": "W1",  "label": "Weekly",  "seconds": 604800},
            {"id": "MN",  "label": "Monthly", "seconds": 2592000},
        ]
    }


@router.get("/assets")
async def get_asset_categories():
    """All tradeable assets by category"""
    return {
        "categories": {
            "forex": {
                "label": "Forex",
                "majors": ["EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD"],
                "minors": ["EURGBP","EURJPY","GBPJPY","AUDJPY","CADJPY","CHFJPY"],
                "exotic": ["USDTRY","USDZAR","USDMXN","USDBRL","USDSGD"],
            },
            "metals": {
                "label": "Metals",
                "symbols": ["XAUUSD","XAGUSD","XPTUSD","XPDUSD","XCUUSD"],
            },
            "energy": {
                "label": "Energy",
                "symbols": ["USOIL","UKOIL","NATGAS","GASOLINE"],
            },
            "indices": {
                "label": "Indices",
                "symbols": ["SPX500","NAS100","US30","GER40","UK100","JPN225","HK50","AUS200"],
            },
            "crypto": {
                "label": "Crypto",
                "top": ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT"],
                "defi": ["UNIUSDT","AAVEUSDT","LINKUSDT","MATICUSDT"],
            },
            "bonds": {
                "label": "Bonds",
                "symbols": ["US2Y","US10Y","US30Y","DE10Y","UK10Y","JP10Y"],
            },
            "commodities": {
                "label": "Commodities",
                "symbols": ["WHEAT","CORN","SOYBEAN","COTTON","COFFEE","SUGAR","LUMBER"],
            },
        }
    }
