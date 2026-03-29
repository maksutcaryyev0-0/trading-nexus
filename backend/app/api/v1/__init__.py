from fastapi import APIRouter

from app.api.v1 import (
    auth, analysis, market, risk, journal,
    notifications, settings_api, academy,
    strategies, calendar, watchlist, ai_chat,
)

router = APIRouter()

router.include_router(auth.router,          prefix="/auth",          tags=["auth"])
router.include_router(analysis.router,      prefix="/analysis",      tags=["analysis"])
router.include_router(market.router,        prefix="/market",        tags=["market"])
router.include_router(risk.router,          prefix="/risk",          tags=["risk"])
router.include_router(journal.router,       prefix="/journal",       tags=["journal"])
router.include_router(notifications.router, prefix="/notifications",  tags=["notifications"])
router.include_router(settings_api.router,  prefix="/settings",      tags=["settings"])
router.include_router(academy.router,       prefix="/academy",       tags=["academy"])
router.include_router(strategies.router,    prefix="/strategies",    tags=["strategies"])
router.include_router(calendar.router,      prefix="/calendar",      tags=["calendar"])
router.include_router(watchlist.router,     prefix="/watchlist",     tags=["watchlist"])
router.include_router(ai_chat.router,       prefix="/ai",            tags=["ai"])
