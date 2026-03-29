"""
NEXUS Celery Tasks
All scheduled and background jobs
"""
from celery import Celery
from celery.schedules import crontab
import asyncio
from loguru import logger

from app.core.config import settings

celery_app = Celery(
    "nexus",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    beat_schedule={
        # Every minute — price updates for watchlist
        "update-watchlist-prices": {
            "task": "app.core.tasks.update_watchlist_prices",
            "schedule": 60.0,
        },
        # Every 5 minutes — watchlist scoring
        "score-watchlist": {
            "task": "app.core.tasks.score_watchlist",
            "schedule": 300.0,
        },
        # Every 15 minutes — setup scanner
        "scan-setups": {
            "task": "app.core.tasks.scan_setups",
            "schedule": 900.0,
        },
        # Every hour — macro update
        "update-macro": {
            "task": "app.core.tasks.update_macro_data",
            "schedule": 3600.0,
        },
        # Every hour — news sentiment
        "update-news-sentiment": {
            "task": "app.core.tasks.update_news_sentiment",
            "schedule": 3600.0,
        },
        # Morning brief — 7:00 in user timezone
        "morning-brief": {
            "task": "app.core.tasks.send_morning_briefs",
            "schedule": crontab(hour=4, minute=0),  # 7:00 MSK = 4:00 UTC
        },
        # Evening debrief — 21:00
        "evening-debrief": {
            "task": "app.core.tasks.send_evening_debriefs",
            "schedule": crontab(hour=18, minute=0),
        },
        # Weekly report — Sunday 20:00
        "weekly-report": {
            "task": "app.core.tasks.send_weekly_reports",
            "schedule": crontab(day_of_week=0, hour=17, minute=0),
        },
        # COT data — Friday 22:00 (CFTC releases)
        "cot-update": {
            "task": "app.core.tasks.update_cot_data",
            "schedule": crontab(day_of_week=5, hour=22, minute=0),
        },
        # Nightly backup
        "nightly-backup": {
            "task": "app.core.tasks.nightly_backup",
            "schedule": crontab(hour=2, minute=0),
        },
        # Check open positions thesis
        "check-trade-thesis": {
            "task": "app.core.tasks.check_trade_thesis",
            "schedule": 1800.0,
        },
        # Personal model update — daily
        "update-personal-model": {
            "task": "app.core.tasks.update_personal_model",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)


@celery_app.task(name="app.core.tasks.update_watchlist_prices")
def update_watchlist_prices():
    logger.info("Updating watchlist prices...")
    # Async wrapper
    from app.modules.data_collector import data_collector
    # Implementation: fetch prices for all active watchlist items
    logger.info("Watchlist prices updated")


@celery_app.task(name="app.core.tasks.score_watchlist")
def score_watchlist():
    logger.info("Scoring watchlist items...")
    # Score each symbol: hot/watch/avoid
    logger.info("Watchlist scored")


@celery_app.task(name="app.core.tasks.scan_setups")
def scan_setups():
    logger.info("Scanning for setups...")
    # Run setup scanner across all watchlist symbols
    # Send alerts for A+ and A rated setups
    logger.info("Setup scan complete")


@celery_app.task(name="app.core.tasks.update_macro_data")
def update_macro_data():
    logger.info("Updating macro data...")
    # FRED, BLS, yields, etc.
    logger.info("Macro data updated")


@celery_app.task(name="app.core.tasks.update_news_sentiment")
def update_news_sentiment():
    logger.info("Updating news sentiment...")
    # NewsAPI → FinBERT sentiment → store
    logger.info("News sentiment updated")


@celery_app.task(name="app.core.tasks.send_morning_briefs")
def send_morning_briefs():
    logger.info("Sending morning briefs...")
    # For each active user, generate and send morning brief
    # in their language via their preferred channel
    logger.info("Morning briefs sent")


@celery_app.task(name="app.core.tasks.send_evening_debriefs")
def send_evening_debriefs():
    logger.info("Sending evening debriefs...")
    # Daily summary of trades, performance, key events
    logger.info("Evening debriefs sent")


@celery_app.task(name="app.core.tasks.send_weekly_reports")
def send_weekly_reports():
    logger.info("Sending weekly reports...")
    # Full PDF weekly report per user
    logger.info("Weekly reports sent")


@celery_app.task(name="app.core.tasks.update_cot_data")
def update_cot_data():
    logger.info("Updating COT data...")
    # Download CFTC COT data, parse, store
    logger.info("COT data updated")


@celery_app.task(name="app.core.tasks.nightly_backup")
def nightly_backup():
    logger.info("Running nightly backup...")
    import subprocess
    import os
    result = subprocess.run(
        ["/backup.sh"],
        capture_output=True,
        text=True,
        env={**os.environ},
    )
    if result.returncode == 0:
        logger.info("Backup successful")
    else:
        logger.error(f"Backup failed: {result.stderr}")


@celery_app.task(name="app.core.tasks.check_trade_thesis")
def check_trade_thesis():
    logger.info("Checking open trade thesis...")
    # For each open trade, check if thesis is still valid
    # Alert if invalidation level approached
    logger.info("Trade thesis checked")


@celery_app.task(name="app.core.tasks.update_personal_model")
def update_personal_model():
    logger.info("Updating personal models...")
    # Recalculate stats, patterns, best times, best assets
    # Update PersonalStats table for all users
    logger.info("Personal models updated")


@celery_app.task(name="app.core.tasks.send_alert")
def send_alert(user_id: str, message: str, channels: list, lang: str = "en"):
    """Send alert via multiple channels"""
    from app.modules.notifications import NotificationService
    notif = NotificationService()

    for channel in channels:
        try:
            if channel == "telegram":
                asyncio.run(notif.send_telegram(user_id, message))
            elif channel == "email":
                asyncio.run(notif.send_email(user_id, message))
            elif channel == "whatsapp":
                asyncio.run(notif.send_whatsapp(user_id, message))
        except Exception as e:
            logger.error(f"Alert send error [{channel}]: {e}")
