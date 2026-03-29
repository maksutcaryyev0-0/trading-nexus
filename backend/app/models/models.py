"""
NEXUS Database Models
All tables for the system
"""
from sqlalchemy import (
    Column, String, Float, Integer, Boolean,
    DateTime, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id            = Column(String, primary_key=True, default=gen_uuid)
    username      = Column(String(50), unique=True, nullable=False)
    email         = Column(String(200), unique=True, nullable=True)
    password_hash = Column(String(200), nullable=False)
    role          = Column(String(20), default="viewer")  # owner/trader/analyst/viewer
    lang          = Column(String(5),  default="en")
    timezone      = Column(String(50), default="UTC")
    is_active     = Column(Boolean, default=True)
    is_blocked    = Column(Boolean, default=False)
    totp_secret   = Column(String(100), nullable=True)
    two_fa_enabled= Column(Boolean, default=False)
    created_at    = Column(DateTime, default=func.now())
    last_login    = Column(DateTime, nullable=True)

    trades         = relationship("Trade",    back_populates="user")
    journal_entries= relationship("Journal",  back_populates="user")
    alerts         = relationship("Alert",    back_populates="user")
    settings       = relationship("UserSettings", back_populates="user", uselist=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id              = Column(String, primary_key=True, default=gen_uuid)
    user_id         = Column(String, ForeignKey("users.id"), unique=True)
    account_balance = Column(Float, default=10000.0)
    risk_pct        = Column(Float, default=1.0)
    max_daily_loss  = Column(Float, default=5.0)
    max_drawdown    = Column(Float, default=10.0)
    max_positions   = Column(Integer, default=5)
    timezone        = Column(String(50), default="UTC")
    lang            = Column(String(5), default="en")
    theme           = Column(String(20), default="dark")
    watchlist       = Column(JSON, default=list)
    notifications   = Column(JSON, default=dict)
    prop_firm_rules = Column(JSON, default=dict)
    constitution    = Column(Text, nullable=True)
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="settings")


class Trade(Base):
    __tablename__ = "trades"

    id             = Column(String, primary_key=True, default=gen_uuid)
    user_id        = Column(String, ForeignKey("users.id"))
    symbol         = Column(String(20), nullable=False)
    direction      = Column(String(10), nullable=False)  # LONG/SHORT
    status         = Column(String(20), default="open")  # open/closed/cancelled
    entry_price    = Column(Float, nullable=False)
    exit_price     = Column(Float, nullable=True)
    stop_loss      = Column(Float, nullable=True)
    take_profit_1  = Column(Float, nullable=True)
    take_profit_2  = Column(Float, nullable=True)
    take_profit_3  = Column(Float, nullable=True)
    position_size  = Column(Float, nullable=False)
    risk_pct       = Column(Float, nullable=True)
    risk_amount    = Column(Float, nullable=True)
    pnl            = Column(Float, nullable=True)
    pnl_r          = Column(Float, nullable=True)
    timeframe      = Column(String(10), nullable=True)
    setup          = Column(String(100), nullable=True)  # ICT/Wyckoff/etc
    regime         = Column(String(50), nullable=True)
    session        = Column(String(20), nullable=True)  # Asian/London/NY
    confluence_score = Column(Integer, nullable=True)
    rating         = Column(String(5),  nullable=True)  # A+/A/B/C
    notes          = Column(Text, nullable=True)
    screenshot_url = Column(String(500), nullable=True)
    broker         = Column(String(50), nullable=True)
    broker_ticket  = Column(String(100), nullable=True)
    ai_analysis    = Column(JSON, nullable=True)
    autopsy        = Column(JSON, nullable=True)
    tags           = Column(JSON, default=list)
    opened_at      = Column(DateTime, default=func.now())
    closed_at      = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="trades")


class Journal(Base):
    __tablename__ = "journal_entries"

    id         = Column(String, primary_key=True, default=gen_uuid)
    user_id    = Column(String, ForeignKey("users.id"))
    type       = Column(String(30), default="note")  # note/mood/analysis/missed/diary
    title      = Column(String(200), nullable=True)
    content    = Column(Text, nullable=False)
    symbol     = Column(String(20), nullable=True)
    mood_score = Column(Integer, nullable=True)  # 1-10
    energy     = Column(Integer, nullable=True)  # 1-10
    focus      = Column(Integer, nullable=True)  # 1-10
    voice_url  = Column(String(500), nullable=True)
    tags       = Column(JSON, default=list)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="journal_entries")


class Signal(Base):
    __tablename__ = "signals"

    id               = Column(String, primary_key=True, default=gen_uuid)
    user_id          = Column(String, ForeignKey("users.id"))
    symbol           = Column(String(20), nullable=False)
    direction        = Column(String(10), nullable=False)
    confluence_score = Column(Integer, nullable=True)
    rating           = Column(String(5), nullable=True)
    entry_zone_low   = Column(Float, nullable=True)
    entry_zone_high  = Column(Float, nullable=True)
    stop_loss        = Column(Float, nullable=True)
    take_profit_1    = Column(Float, nullable=True)
    take_profit_2    = Column(Float, nullable=True)
    take_profit_3    = Column(Float, nullable=True)
    risk_reward      = Column(Float, nullable=True)
    setup_type       = Column(String(100), nullable=True)
    regime           = Column(String(50), nullable=True)
    status           = Column(String(20), default="pending")  # pending/taken/missed/expired
    result_pnl_r     = Column(Float, nullable=True)
    analysis         = Column(JSON, nullable=True)
    created_at       = Column(DateTime, default=func.now())
    expires_at       = Column(DateTime, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id         = Column(String, primary_key=True, default=gen_uuid)
    user_id    = Column(String, ForeignKey("users.id"))
    type       = Column(String(50), nullable=False)
    symbol     = Column(String(20), nullable=True)
    title      = Column(String(200), nullable=False)
    message    = Column(Text, nullable=False)
    priority   = Column(String(20), default="normal")  # critical/high/normal/low
    channels   = Column(JSON, default=list)  # telegram/email/sms/discord
    sent       = Column(Boolean, default=False)
    sent_at    = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="alerts")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id          = Column(String, primary_key=True, default=gen_uuid)
    user_id     = Column(String, ForeignKey("users.id"))
    filename    = Column(String(300), nullable=False)
    title       = Column(String(300), nullable=True)
    category    = Column(String(100), nullable=True)  # strategy/macro/psychology/etc
    file_type   = Column(String(20), nullable=False)  # pdf/txt/docx/csv
    file_size   = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)
    indexed     = Column(Boolean, default=False)
    summary     = Column(Text, nullable=True)
    tags        = Column(JSON, default=list)
    created_at  = Column(DateTime, default=func.now())


class ApiKey(Base):
    __tablename__ = "api_keys"

    id           = Column(String, primary_key=True, default=gen_uuid)
    user_id      = Column(String, ForeignKey("users.id"))
    service      = Column(String(100), nullable=False)
    key_encrypted= Column(Text, nullable=False)
    is_active    = Column(Boolean, default=True)
    last_tested  = Column(DateTime, nullable=True)
    test_status  = Column(String(20), nullable=True)  # ok/error/rate_limited
    created_at   = Column(DateTime, default=func.now())


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id           = Column(String, primary_key=True, default=gen_uuid)
    user_id      = Column(String, ForeignKey("users.id"))
    symbol       = Column(String(20), nullable=False)
    category     = Column(String(50), nullable=True)
    score        = Column(Integer, nullable=True)
    status       = Column(String(20), default="watch")  # hot/watch/avoid
    notes        = Column(Text, nullable=True)
    last_analysis= Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=func.now())


class StrategyRule(Base):
    __tablename__ = "strategy_rules"

    id          = Column(String, primary_key=True, default=gen_uuid)
    user_id     = Column(String, ForeignKey("users.id"))
    name        = Column(String(200), nullable=False)
    type        = Column(String(50), nullable=False)  # builtin/custom
    description = Column(Text, nullable=True)
    rules_json  = Column(JSON, nullable=True)
    symbols     = Column(JSON, default=list)
    timeframes  = Column(JSON, default=list)
    is_active   = Column(Boolean, default=True)
    win_rate    = Column(Float, nullable=True)
    total_trades= Column(Integer, default=0)
    created_at  = Column(DateTime, default=func.now())


class PersonalStats(Base):
    __tablename__ = "personal_stats"

    id              = Column(String, primary_key=True, default=gen_uuid)
    user_id         = Column(String, ForeignKey("users.id"), unique=True)
    total_trades    = Column(Integer, default=0)
    winning_trades  = Column(Integer, default=0)
    losing_trades   = Column(Integer, default=0)
    win_rate        = Column(Float, default=0.0)
    avg_win_r       = Column(Float, default=0.0)
    avg_loss_r      = Column(Float, default=0.0)
    profit_factor   = Column(Float, default=0.0)
    total_pnl       = Column(Float, default=0.0)
    max_drawdown    = Column(Float, default=0.0)
    best_symbol     = Column(String(20), nullable=True)
    best_session    = Column(String(20), nullable=True)
    best_setup      = Column(String(100), nullable=True)
    best_day_of_week= Column(String(20), nullable=True)
    best_hour       = Column(Integer, nullable=True)
    error_patterns  = Column(JSON, default=dict)
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())
