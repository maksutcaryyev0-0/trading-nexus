"""
NEXUS Risk Engine
Position sizing, daily limits, kill switch, prop firm guardian
"""
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class RiskParams:
    account_balance: float
    risk_pct: float = 1.0
    max_daily_loss_pct: float = 5.0
    max_drawdown_pct: float = 10.0
    max_positions: int = 5
    max_correlated_risk_pct: float = 3.0
    kelly_fraction: float = 0.25


@dataclass
class PositionResult:
    allowed: bool
    position_size: float
    risk_amount: float
    risk_pct: float
    reason: str
    warnings: list


class RiskEngine:

    def __init__(self):
        self.kill_switch_active = False
        self.daily_pnl = {}
        self.open_positions = {}

    def calculate_position(
        self,
        params: RiskParams,
        entry: float,
        stop: float,
        symbol: str,
        user_id: str,
        confidence_score: int = 50,
        data_quality: str = "OBSERVED",
    ) -> PositionResult:

        warnings = []

        # Kill switch check
        if self.kill_switch_active:
            return PositionResult(
                allowed=False,
                position_size=0,
                risk_amount=0,
                risk_pct=0,
                reason="KILL SWITCH IS ACTIVE — /resume to unlock",
                warnings=[],
            )

        # Daily loss check
        daily_pnl = self.daily_pnl.get(user_id, 0)
        daily_loss_pct = abs(daily_pnl) / params.account_balance * 100
        if daily_pnl < 0 and daily_loss_pct >= params.max_daily_loss_pct:
            return PositionResult(
                allowed=False,
                position_size=0,
                risk_amount=0,
                risk_pct=0,
                reason=f"Daily loss limit reached: {daily_loss_pct:.1f}%",
                warnings=[],
            )

        # Max positions check
        user_positions = self.open_positions.get(user_id, [])
        if len(user_positions) >= params.max_positions:
            return PositionResult(
                allowed=False,
                position_size=0,
                risk_amount=0,
                risk_pct=0,
                reason=f"Max positions reached: {params.max_positions}",
                warnings=[],
            )

        # Calculate stop distance
        if entry <= 0 or stop <= 0:
            return PositionResult(
                allowed=False,
                position_size=0,
                risk_amount=0,
                risk_pct=0,
                reason="Invalid entry or stop levels",
                warnings=[],
            )

        stop_distance = abs(entry - stop)
        stop_pct = stop_distance / entry * 100

        if stop_pct < 0.01:
            return PositionResult(
                allowed=False,
                position_size=0,
                risk_amount=0,
                risk_pct=0,
                reason="Stop too tight — minimum 0.01%",
                warnings=[],
            )

        # Adjust risk for data quality
        risk_multiplier = 1.0
        if data_quality == "SPECULATIVE":
            risk_multiplier = 0.5
            warnings.append("Data quality SPECULATIVE — risk halved")
        elif data_quality == "INFERRED":
            risk_multiplier = 0.75
            warnings.append("Data quality INFERRED — risk reduced 25%")

        # Adjust for confidence score
        if confidence_score < 50:
            risk_multiplier *= 0.5
            warnings.append(f"Low confluence ({confidence_score}/100) — risk halved")
        elif confidence_score < 65:
            risk_multiplier *= 0.75
            warnings.append(f"Medium confluence ({confidence_score}/100) — risk reduced")

        # Daily loss warning
        if daily_pnl < 0 and daily_loss_pct >= params.max_daily_loss_pct * 0.7:
            risk_multiplier *= 0.5
            warnings.append(f"Approaching daily limit ({daily_loss_pct:.1f}%) — risk halved")

        # Calculate final position
        adjusted_risk_pct = params.risk_pct * risk_multiplier
        risk_amount = params.account_balance * (adjusted_risk_pct / 100)
        position_size = risk_amount / stop_distance

        # Warning if stop is wide
        if stop_pct > 3:
            warnings.append(f"Wide stop ({stop_pct:.1f}%) — consider tighter entry")

        return PositionResult(
            allowed=True,
            position_size=round(position_size, 4),
            risk_amount=round(risk_amount, 2),
            risk_pct=round(adjusted_risk_pct, 2),
            reason="Position approved",
            warnings=warnings,
        )

    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        fraction: float = 0.25,
    ) -> float:
        """Kelly Criterion position sizing"""
        if avg_loss == 0:
            return 0
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p
        kelly = (b * p - q) / b
        return max(0, kelly * fraction)

    def var_calculation(
        self,
        returns: list,
        confidence: float = 0.95,
    ) -> dict:
        """Value at Risk calculation"""
        import numpy as np
        if not returns:
            return {"var_95": 0, "var_99": 0, "cvar_95": 0}
        arr = np.array(returns)
        var_95 = float(np.percentile(arr, (1 - 0.95) * 100))
        var_99 = float(np.percentile(arr, (1 - 0.99) * 100))
        cvar_95 = float(arr[arr <= var_95].mean()) if len(arr[arr <= var_95]) > 0 else var_95
        return {
            "var_95": round(var_95, 4),
            "var_99": round(var_99, 4),
            "cvar_95": round(cvar_95, 4),
        }

    def risk_of_ruin(
        self,
        win_rate: float,
        risk_pct: float,
        ruin_threshold: float = 50.0,
    ) -> float:
        """Probability of reaching ruin threshold"""
        if win_rate <= 0 or win_rate >= 1:
            return 1.0 if win_rate <= 0 else 0.0
        edge = win_rate - (1 - win_rate)
        if edge <= 0:
            return 1.0
        r = (1 - win_rate) / win_rate
        n = ruin_threshold / risk_pct
        ror = r ** n
        return round(min(ror, 1.0), 4)

    def activate_kill_switch(self, user_id: str, reason: str):
        self.kill_switch_active = True
        logger.warning(f"KILL SWITCH activated by {user_id}: {reason}")

    def deactivate_kill_switch(self, user_id: str):
        self.kill_switch_active = False
        logger.info(f"Kill switch deactivated by {user_id}")

    def check_psychology_block(self, session_stats: dict) -> tuple[bool, str]:
        """Block trading based on psychological signals"""
        consecutive_losses = session_stats.get("consecutive_losses", 0)
        trades_today = session_stats.get("trades_today", 0)
        daily_pnl_pct = session_stats.get("daily_pnl_pct", 0)
        hours_trading = session_stats.get("hours_trading", 0)

        if consecutive_losses >= 3:
            return True, f"3 consecutive losses — mandatory 2-hour pause"
        if trades_today >= 10:
            return True, f"10 trades today — daily limit reached"
        if daily_pnl_pct <= -3:
            return True, f"Daily loss {daily_pnl_pct:.1f}% — stop trading today"
        if hours_trading >= 6:
            return True, f"6+ hours trading — cognitive fatigue risk"

        return False, "OK"

    def correlation_check(
        self, open_positions: list, new_symbol: str
    ) -> dict:
        """Check hidden correlation risk"""
        correlated_groups = {
            "usd_positive": ["DXY", "USDJPY", "USDCHF", "USDCAD"],
            "usd_negative": ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "XAUUSD"],
            "risk_on": ["AUDUSD", "NZDUSD", "GBPUSD", "SPX", "NAS100"],
            "risk_off": ["XAUUSD", "USDJPY", "USDCHF", "VIX"],
            "crypto": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        }

        new_groups = [
            g for g, syms in correlated_groups.items()
            if new_symbol.upper() in syms
        ]

        conflicts = []
        for pos in open_positions:
            pos_symbol = pos.get("symbol", "")
            pos_groups = [
                g for g, syms in correlated_groups.items()
                if pos_symbol.upper() in syms
            ]
            for g in new_groups:
                if g in pos_groups:
                    conflicts.append({
                        "symbol": pos_symbol,
                        "group": g,
                        "warning": f"Correlated with {pos_symbol} via {g}",
                    })

        return {
            "has_correlation": len(conflicts) > 0,
            "conflicts": conflicts,
            "warning": (
                f"High correlation with {len(conflicts)} open position(s)"
                if conflicts else "No significant correlation detected"
            ),
        }


risk_engine = RiskEngine()
