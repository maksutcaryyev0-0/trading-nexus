from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.modules.ai_war_room import ai_war_room
from app.modules.knowledge_base import knowledge_base

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    lang: str = "en"
    symbol: Optional[str] = None
    context: str = "dashboard"


class MorningBriefRequest(BaseModel):
    lang: str = "en"
    timezone: str = "UTC"
    user_id: str = "admin"


class AutopsyRequest(BaseModel):
    trade: dict
    lang: str = "en"


class PsychologyRequest(BaseModel):
    session_data: dict
    lang: str = "en"


class KnowledgeSearchRequest(BaseModel):
    query: str
    user_id: str = "admin"
    category: Optional[str] = None


@router.post("/chat")
async def ai_chat(req: ChatRequest):
    """Free-form AI chat — knows your trades, books, strategies"""
    symbol  = req.symbol or "MARKET"
    context = await knowledge_base.search(req.message, "admin", limit=3)
    context_text = ""
    if context:
        context_text = "\n\nRelevant from your knowledge base:\n" + \
            "\n".join([f"- {r['text'][:200]}" for r in context])

    full_message = req.message + context_text
    answer = await ai_war_room.quick_analysis(
        symbol=symbol,
        question=full_message,
        lang=req.lang,
    )
    return {"answer": answer, "context_used": len(context) > 0}


@router.post("/morning-brief")
async def morning_brief(req: MorningBriefRequest):
    """Generate morning briefing"""
    user_data = {
        "lang":     req.lang,
        "timezone": req.timezone,
        "user_id":  req.user_id,
    }
    brief = await ai_war_room.morning_brief(user_data, req.lang, req.timezone)
    return {"brief": brief}


@router.post("/autopsy")
async def trade_autopsy(req: AutopsyRequest):
    """AI trade autopsy after close"""
    result = await ai_war_room.trade_autopsy(req.trade, req.lang)
    return result


@router.post("/psychology")
async def psychology_check(req: PsychologyRequest):
    """Psychology coaching"""
    result = await ai_war_room.psychology_coach(req.session_data, req.lang)
    return result


@router.post("/knowledge/search")
async def knowledge_search(req: KnowledgeSearchRequest):
    """Search knowledge base"""
    results = await knowledge_base.search(req.query, req.user_id, limit=5)
    return {"results": results, "count": len(results)}


@router.get("/models")
async def available_models():
    """List configured AI models"""
    from app.core.config import settings
    return {"models": settings.available_ai_models}
