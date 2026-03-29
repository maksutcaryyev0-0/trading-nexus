from fastapi import APIRouter
from app.api.v1._stubs import (
    router_market, router_journal, router_calendar,
    router_watchlist, router_strategies, router_academy,
    router_notifications, router_settings,
)

# Re-export all routers
market        = type('m', (), {'router': router_market})()
journal       = type('m', (), {'router': router_journal})()
calendar      = type('m', (), {'router': router_calendar})()
watchlist     = type('m', (), {'router': router_watchlist})()
strategies    = type('m', (), {'router': router_strategies})()
academy       = type('m', (), {'router': router_academy})()
notifications = type('m', (), {'router': router_notifications})()
settings_api  = type('m', (), {'router': router_settings})()
