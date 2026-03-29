from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.modules.risk_engine import risk_engine, RiskParams

router = APIRouter()


class PositionRequest(BaseModel):
    account_balance: float
    risk_pct: float = 1.0
    entry: float
    stop: float
    symbol: str
    confidence_score: int = 50
    data_quality: str = "OBSERVED"
    max_daily_loss_pct: float = 5.0
    max_drawdown_pct: float = 10.0
    max_positions: int = 5


class KillSwitchRequest(BaseModel):
    action: str  # activate / deactivate
    reason: Optional[str] = "Manual"


class PsychBlockRequest(BaseModel):
    consecutive_losses: int = 0
    trades_today: int = 0
    daily_pnl_pct: float = 0.0
    hours_trading: float = 0.0


class VarRequest(BaseModel):
    returns: list
    confidence: float = 0.95


class KellyRequest(BaseModel):
    win_rate: float
    avg_win: float
    avg_loss: float
    fraction: float = 0.25


@router.post("/position-size")
async def calculate_position(req: PositionRequest):
    params = RiskParams(
        account_balance=req.account_balance,
        risk_pct=req.risk_pct,
        max_daily_loss_pct=req.max_daily_loss_pct,
        max_drawdown_pct=req.max_drawdown_pct,
        max_positions=req.max_positions,
    )
    result = risk_engine.calculate_position(
        params=params,
        entry=req.entry,
        stop=req.stop,
        symbol=req.symbol,
        user_id="current_user",
        confidence_score=req.confidence_score,
        data_quality=req.data_quality,
    )
    return {
        "allowed":       result.allowed,
        "position_size": result.position_size,
        "risk_amount":   result.risk_amount,
        "risk_pct":      result.risk_pct,
        "reason":        result.reason,
        "warnings":      result.warnings,
    }


@router.post("/kill-switch")
async def kill_switch(req: KillSwitchRequest):
    if req.action == "activate":
        risk_engine.activate_kill_switch("api_user", req.reason or "API call")
        return {"status": "activated", "message": "All trading stopped"}
    else:
        risk_engine.deactivate_kill_switch("api_user")
        return {"status": "deactivated", "message": "Trading resumed"}


@router.get("/kill-switch/status")
async def kill_switch_status():
    return {"active": risk_engine.kill_switch_active}


@router.post("/psychology-check")
async def psychology_check(req: PsychBlockRequest):
    blocked, reason = risk_engine.check_psychology_block({
        "consecutive_losses": req.consecutive_losses,
        "trades_today":       req.trades_today,
        "daily_pnl_pct":      req.daily_pnl_pct,
        "hours_trading":      req.hours_trading,
    })
    return {"blocked": blocked, "reason": reason}


@router.post("/var")
async def calculate_var(req: VarRequest):
    return risk_engine.var_calculation(req.returns, req.confidence)


@router.post("/kelly")
async def kelly_criterion(req: KellyRequest):
    kelly = risk_engine.kelly_criterion(
        req.win_rate, req.avg_win, req.avg_loss, req.fraction
    )
    return {
        "kelly_pct":     round(kelly * 100, 2),
        "full_kelly":    round(kelly * 100 / req.fraction, 2),
        "recommended":   f"{round(kelly * 100, 2)}% of account",
    }


@router.post("/risk-of-ruin")
async def risk_of_ruin(data: dict):
    ror = risk_engine.risk_of_ruin(
        win_rate=data.get("win_rate", 0.5),
        risk_pct=data.get("risk_pct", 1.0),
        ruin_threshold=data.get("ruin_threshold", 50.0),
    )
    return {
        "risk_of_ruin":     ror,
        "risk_of_ruin_pct": round(ror * 100, 2),
        "safe":             ror < 0.01,
    }


@router.post("/correlation-check")
async def correlation_check(data: dict):
    result = risk_engine.correlation_check(
        data.get("open_positions", []),
        data.get("new_symbol", ""),
    )
    return result
