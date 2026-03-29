"""
NEXUS Data Collector
All market data sources with automatic fallback
"""
import asyncio
from typing import Optional
import httpx
import yfinance as yf
from loguru import logger

from app.core.config import settings


class DataCollector:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self._cache = {}

    async def get_price(self, symbol: str) -> dict:
        """Get price with automatic fallback across sources"""
        sources = [
            self._twelve_data,
            self._alpha_vantage,
            self._yahoo_finance,
            self._stooq,
        ]
        for source in sources:
            try:
                data = await source(symbol)
                if data and data.get("price"):
                    return data
            except Exception as e:
                logger.debug(f"{source.__name__} failed for {symbol}: {e}")
                continue
        return {"price": None, "quality": "UNAVAILABLE", "symbol": symbol}

    async def _twelve_data(self, symbol: str) -> Optional[dict]:
        if not settings.TWELVE_DATA_KEY:
            return None
        url = f"https://api.twelvedata.com/price"
        params = {"symbol": symbol, "apikey": settings.TWELVE_DATA_KEY}
        r = await self.client.get(url, params=params)
        data = r.json()
        if "price" in data:
            return {
                "price": float(data["price"]),
                "symbol": symbol,
                "source": "twelvedata",
                "quality": "OBSERVED",
            }
        return None

    async def _alpha_vantage(self, symbol: str) -> Optional[dict]:
        if not settings.ALPHA_VANTAGE_KEY:
            return None
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_KEY,
        }
        r = await self.client.get(url, params=params)
        data = r.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        if price:
            return {
                "price": float(price),
                "symbol": symbol,
                "source": "alphavantage",
                "quality": "OBSERVED",
            }
        return None

    async def _yahoo_finance(self, symbol: str) -> Optional[dict]:
        try:
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            hist = await asyncio.to_thread(
                ticker.history, period="1d", interval="1m"
            )
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                return {
                    "price": price,
                    "symbol": symbol,
                    "source": "yahoo",
                    "quality": "OBSERVED",
                }
        except Exception:
            pass
        return None

    async def _stooq(self, symbol: str) -> Optional[dict]:
        """Free fallback — no API key needed"""
        stooq_sym = symbol.replace("/", "").replace("USDT", "-USD").lower()
        url = f"https://stooq.com/q/l/?s={stooq_sym}&f=sd2t2ohlcv&h&e=csv"
        try:
            r = await self.client.get(url)
            lines = r.text.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split(",")
                if len(parts) >= 5:
                    price = float(parts[4])
                    return {
                        "price": price,
                        "symbol": symbol,
                        "source": "stooq",
                        "quality": "DERIVED",
                    }
        except Exception:
            pass
        return None

    async def get_ohlcv(
        self, symbol: str, timeframe: str = "1h", limit: int = 200
    ) -> list:
        """OHLCV data for chart and analysis"""
        try:
            import ccxt.async_support as ccxt
            if "USDT" in symbol or "BTC" in symbol:
                exchange = ccxt.binance()
                tf_map = {
                    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                    "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w",
                }
                tf = tf_map.get(timeframe, "1h")
                candles = await exchange.fetch_ohlcv(symbol, tf, limit=limit)
                await exchange.close()
                return [
                    {
                        "timestamp": c[0],
                        "open": c[1],
                        "high": c[2],
                        "low": c[3],
                        "close": c[4],
                        "volume": c[5],
                    }
                    for c in candles
                ]
        except Exception as e:
            logger.debug(f"CCXT error: {e}")

        # Fallback to yfinance
        try:
            yf_tf_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "60m", "4h": "1h", "1d": "1d", "1w": "1wk",
            }
            period_map = {
                "1m": "1d", "5m": "5d", "15m": "5d", "30m": "1mo",
                "1h": "1mo", "4h": "3mo", "1d": "1y", "1w": "5y",
            }
            interval = yf_tf_map.get(timeframe, "60m")
            period = period_map.get(timeframe, "1mo")
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            hist = await asyncio.to_thread(
                ticker.history, period=period, interval=interval
            )
            if not hist.empty:
                return [
                    {
                        "timestamp": int(idx.timestamp() * 1000),
                        "open": row["Open"],
                        "high": row["High"],
                        "low": row["Low"],
                        "close": row["Close"],
                        "volume": row["Volume"],
                    }
                    for idx, row in hist.iterrows()
                ]
        except Exception as e:
            logger.debug(f"yfinance error: {e}")

        return []

    async def get_macro(self, series_id: str) -> dict:
        """FRED macro data"""
        if not settings.FRED_API_KEY:
            return {"data": [], "source": "FRED not configured"}
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": settings.FRED_API_KEY,
            "file_type": "json",
            "limit": 12,
            "sort_order": "desc",
        }
        try:
            r = await self.client.get(url, params=params)
            data = r.json()
            obs = data.get("observations", [])
            return {
                "series_id": series_id,
                "data": [
                    {"date": o["date"], "value": o["value"]}
                    for o in obs if o["value"] != "."
                ],
                "source": "FRED",
                "quality": "OBSERVED",
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_cot_data(self) -> dict:
        """CFTC COT data — free, no API key"""
        url = "https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2024/futures/fin_fut_csv_2024.zip"
        return {
            "source": "CFTC",
            "note": "Download manually from cftc.gov or use paid API",
            "quality": "OBSERVED",
        }

    async def get_fear_greed(self) -> dict:
        """Fear & Greed — free, no API key"""
        tasks = [self._crypto_fg(), self._equity_fg()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            "crypto": results[0] if not isinstance(results[0], Exception) else None,
            "equity": results[1] if not isinstance(results[1], Exception) else None,
        }

    async def _crypto_fg(self) -> dict:
        r = await self.client.get("https://api.alternative.me/fng/")
        data = r.json()
        fg = data["data"][0]
        return {
            "value": int(fg["value"]),
            "classification": fg["value_classification"],
        }

    async def _equity_fg(self) -> dict:
        return {"note": "CNN Fear & Greed — scraping required"}

    async def get_news(self, query: str, lang: str = "en") -> list:
        """News from multiple sources with fallback"""
        results = []
        if settings.NEWS_API_KEY:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "language": lang[:2],
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "apiKey": settings.NEWS_API_KEY,
                }
                r = await self.client.get(url, params=params)
                data = r.json()
                for article in data.get("articles", []):
                    results.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "url": article["url"],
                        "published": article["publishedAt"],
                        "source": article["source"]["name"],
                    })
            except Exception as e:
                logger.debug(f"NewsAPI error: {e}")

        # Free fallback — Reuters RSS
        if not results:
            try:
                rss_url = "https://feeds.reuters.com/reuters/businessNews"
                r = await self.client.get(rss_url)
                results.append({
                    "title": "Reuters RSS (parsed)",
                    "source": "Reuters",
                    "note": "Implement XML parsing for full feed",
                })
            except Exception:
                pass

        return results

    async def get_economic_calendar(self) -> list:
        """Economic calendar — free sources"""
        events = []
        try:
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            r = await self.client.get(url)
            data = r.json()
            for event in data:
                events.append({
                    "title": event.get("title"),
                    "country": event.get("country"),
                    "date": event.get("date"),
                    "time": event.get("time"),
                    "impact": event.get("impact"),
                    "forecast": event.get("forecast"),
                    "previous": event.get("previous"),
                })
        except Exception as e:
            logger.debug(f"Calendar error: {e}")
        return events

    async def close(self):
        await self.client.aclose()


data_collector = DataCollector()
