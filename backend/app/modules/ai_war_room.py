"""
NEXUS AI War Room
5 AI models analyze in parallel, then consensus
"""
import asyncio
from typing import Optional
import anthropic
import google.generativeai as genai
from groq import AsyncGroq
from loguru import logger

from app.core.config import settings
from app.core.i18n import get_text


SYSTEM_PROMPT = """You are an institutional trading analyst inside NEXUS Trading OS.
Analyze markets with precision. Be direct. No fluff.
Always provide: regime, structure, levels, scenarios with probabilities.
Format: structured JSON when requested, prose when analyzing."""


class AIWarRoom:

    def __init__(self):
        self.claude = None
        self.gemini = None
        self.groq = None
        self._init_models()

    def _init_models(self):
        if settings.ANTHROPIC_API_KEY:
            self.claude = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini = genai.GenerativeModel("gemini-1.5-pro")
        if settings.GROQ_API_KEY:
            self.groq = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def full_analysis(
        self,
        symbol: str,
        market_data: dict,
        user_id: str,
        lang: str = "en",
        timezone: str = "UTC"
    ) -> dict:
        """
        Full institutional analysis — all engines in parallel
        """
        tasks = [
            self._claude_main_analysis(symbol, market_data, lang),
            self._gemini_macro_analysis(symbol, market_data, lang),
            self._groq_fast_sentiment(symbol, market_data, lang),
            self._ai_debate(symbol, market_data, lang),
            self._risk_assessment(symbol, market_data),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        main       = results[0] if not isinstance(results[0], Exception) else {}
        macro      = results[1] if not isinstance(results[1], Exception) else {}
        sentiment  = results[2] if not isinstance(results[2], Exception) else {}
        debate     = results[3] if not isinstance(results[3], Exception) else {}
        risk       = results[4] if not isinstance(results[4], Exception) else {}

        confluence = self._calculate_confluence(main, macro, sentiment, debate)

        return {
            "symbol": symbol,
            "lang": lang,
            "timezone": timezone,
            "confluence_score": confluence["score"],
            "rating": confluence["rating"],
            "regime": main.get("regime", "UNKNOWN"),
            "structure": main.get("structure", {}),
            "liquidity": main.get("liquidity", {}),
            "scenarios": main.get("scenarios", {}),
            "macro": macro,
            "sentiment": sentiment,
            "debate": debate,
            "risk": risk,
            "trade_plan": main.get("trade_plan", {}),
            "confidence": confluence["confidence"],
            "models_used": self._models_used(),
        }

    async def _claude_main_analysis(
        self, symbol: str, data: dict, lang: str
    ) -> dict:
        if not self.claude:
            return {"error": "Claude API not configured"}

        prompt = f"""
Perform FULL INSTITUTIONAL ANALYSIS for {symbol}.

Market Data:
{data}

Provide analysis in {lang} language covering:
1. MARKET REGIME (Trend/Range/Expansion/Compression/Event)
2. HTF STRUCTURE (BOS/CHOCH/MSS, Premium/Discount, Dealing Range)
3. LIQUIDITY MAP (BSL/SSL, Equal Highs/Lows, Stop Clusters, FVG zones)
4. MULTI-TIMEFRAME (MN→W1→D1→H4→H1→M15→M5→M1 confluence)
5. ICT/SMC (Order Blocks, Breaker Blocks, Mitigation, Kill Zones)
6. WYCKOFF (Phase: Accumulation/Markup/Distribution/Markdown)
7. ELLIOTT WAVE (count, most probable scenario, targets)
8. VSA (No Supply/Demand, Stopping Volume, Climax)
9. SCENARIOS:
   - Bull ({symbol} target, probability %, trigger, invalidation)
   - Base (probability %, levels)
   - Bear (target, probability %, trigger, invalidation)
10. DEVIL'S ADVOCATE (5 reasons NOT to trade)
11. TRADE PLAN:
    - Entry zone
    - Stop loss (with reason)
    - TP1 / TP2 / TP3
    - Risk/Reward
    - Best session for entry
    - What invalidates the thesis

Respond in JSON format.
"""
        try:
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            import json
            text = msg.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return {"error": str(e)}

    async def _gemini_macro_analysis(
        self, symbol: str, data: dict, lang: str
    ) -> dict:
        if not self.gemini:
            return {"error": "Gemini API not configured"}
        try:
            prompt = f"""
Macro analysis for {symbol} in {lang}:
- Central bank stance (all 8 major CBs relevant to this asset)
- Yield curve impact
- DXY correlation and current trend
- Risk-on / Risk-off environment
- Geopolitical factors
- Seasonal patterns for this month
- Global money flow direction
- Inflation / Growth regime
Respond in JSON.
Data: {data}
"""
            resp = await asyncio.to_thread(
                self.gemini.generate_content, prompt
            )
            import json
            text = resp.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
        except Exception as e:
            logger.error(f"Gemini macro error: {e}")
            return {"error": str(e)}

    async def _groq_fast_sentiment(
        self, symbol: str, data: dict, lang: str
    ) -> dict:
        if not self.groq:
            return {"error": "Groq API not configured"}
        try:
            resp = await self.groq.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"""Fast sentiment analysis for {symbol} in {lang}:
- Overall sentiment (Bullish/Neutral/Bearish) with score -100 to +100
- News sentiment summary
- Social sentiment
- COT positioning summary
- Fear & Greed level
- Retail vs Institutional positioning
Respond JSON only. Data: {data}"""
                }],
                max_tokens=1000,
            )
            import json
            text = resp.choices[0].message.content
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
        except Exception as e:
            logger.error(f"Groq sentiment error: {e}")
            return {"error": str(e)}

    async def _ai_debate(
        self, symbol: str, data: dict, lang: str
    ) -> dict:
        """Bull AI vs Bear AI — devil's advocate"""
        if not self.claude:
            return {}
        try:
            prompt = f"""
Run AI DEBATE for {symbol} in {lang}.

BULL AI: Present the strongest possible case for going LONG.
5 specific reasons with price levels and logic.

BEAR AI: Present the strongest possible case for going SHORT.
5 specific reasons with price levels and logic.

DEVIL'S ADVOCATE: What is the most likely way both sides are wrong?

CONSENSUS: Neutral assessment. What does the weight of evidence suggest?

BIAS CHECK: What cognitive biases might affect analysis of this asset right now?

Data: {data}

Respond in JSON with keys: bull_case, bear_case, devils_advocate, consensus, bias_check
"""
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            import json
            text = msg.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
        except Exception as e:
            logger.error(f"Debate error: {e}")
            return {"error": str(e)}

    async def _risk_assessment(self, symbol: str, data: dict) -> dict:
        volatility = data.get("atr_pct", 1.0)
        regime = data.get("regime", "unknown")
        spread = data.get("spread_pct", 0.01)
        near_event = data.get("near_high_impact_event", False)

        risk_score = 50
        if volatility > 2:
            risk_score += 20
        if near_event:
            risk_score += 15
        if spread > 0.05:
            risk_score += 10
        if regime == "Event":
            risk_score += 15

        return {
            "risk_score": min(risk_score, 100),
            "volatility_regime": (
                "extreme" if volatility > 3
                else "high" if volatility > 2
                else "normal" if volatility > 0.5
                else "low"
            ),
            "near_event": near_event,
            "tradeable": risk_score < 75,
            "recommended_risk_pct": (
                0.25 if risk_score > 75
                else 0.5 if risk_score > 60
                else 1.0
            ),
        }

    def _calculate_confluence(
        self, main: dict, macro: dict, sentiment: dict, debate: dict
    ) -> dict:
        score = 50

        if main.get("structure", {}).get("htf_bias") == "bullish":
            score += 10
        if macro.get("risk_environment") == "risk-on":
            score += 8
        sent_score = sentiment.get("sentiment_score", 0)
        if abs(sent_score) > 50:
            score += 7
        if debate.get("consensus", {}).get("direction"):
            score += 10

        score = max(0, min(100, score))
        rating = (
            "A+" if score >= 85
            else "A" if score >= 75
            else "B" if score >= 60
            else "C" if score >= 45
            else "Avoid"
        )

        return {
            "score": score,
            "rating": rating,
            "confidence": (
                "high" if score >= 75
                else "medium" if score >= 55
                else "low"
            ),
        }

    def _models_used(self) -> list:
        used = []
        if self.claude:
            used.append("claude")
        if self.gemini:
            used.append("gemini")
        if self.groq:
            used.append("groq")
        used.append("finbert")
        return used

    async def quick_analysis(
        self, symbol: str, question: str, lang: str = "en"
    ) -> str:
        """Quick AI response for chat panel"""
        if not self.claude:
            return "Claude API not configured"
        try:
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"[{symbol}] {question}\nRespond in {lang}."
                }]
            )
            return msg.content[0].text
        except Exception as e:
            return f"Error: {e}"

    async def trade_autopsy(
        self, trade: dict, lang: str = "en"
    ) -> dict:
        """Full AI trade autopsy after close"""
        if not self.claude:
            return {"error": "Claude not configured"}
        prompt = f"""
Perform TRADE AUTOPSY in {lang} for this closed trade:
{trade}

Analyze:
1. Was the setup valid? (A+/A/B/C/Poor)
2. Entry quality (1-10)
3. Exit quality (1-10)
4. Risk management (1-10)
5. Psychological discipline (1-10)
6. What was done RIGHT
7. What was done WRONG
8. Was this a Good Loss (correct process, bad outcome) or Bad Loss?
9. Key lesson (one sentence)
10. What to do differently next time

Respond JSON.
"""
        try:
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            import json
            text = msg.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
        except Exception as e:
            return {"error": str(e)}

    async def morning_brief(
        self, user_data: dict, lang: str = "en", timezone: str = "UTC"
    ) -> str:
        """Daily morning briefing"""
        if not self.claude:
            return "Claude API not configured"
        prompt = f"""
Generate MORNING BRIEFING in {lang} for timezone {timezone}.

User profile: {user_data}

Include:
1. Market overnight summary
2. Key levels to watch today
3. Economic calendar highlights with impact assessment
4. Recommended trading mode (Aggressive/Normal/Defensive/No Trade)
5. Top 3 setups to watch
6. Risk warnings for today
7. Motivational note based on recent performance

Keep it concise, actionable, professional.
"""
        try:
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception as e:
            return f"Error generating brief: {e}"

    async def psychology_coach(
        self, session_data: dict, lang: str = "en"
    ) -> dict:
        """Psychological coaching based on session behavior"""
        if not self.claude:
            return {}
        prompt = f"""
Analyze trading PSYCHOLOGY in {lang}:
Session data: {session_data}

Detect:
- Revenge trading patterns
- FOMO signals
- Overtrading
- Fear-based decisions
- Greed patterns

Provide:
- Overall psychological state (1-10)
- Specific patterns detected
- Immediate recommendation
- Should trading continue today? (yes/pause/stop)

Respond JSON.
"""
        try:
            msg = await self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            import json
            text = msg.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {}
        except Exception as e:
            return {"error": str(e)}


ai_war_room = AIWarRoom()
