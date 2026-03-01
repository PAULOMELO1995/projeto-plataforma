from dataclasses import dataclass

PLATFORM_RATE_BRL = 6.0
MIN_WITHDRAW_USD = 20.0


@dataclass(frozen=True)
class MachinePlan:
    id: str
    name: str
    contract_value_usd: float
    duration_days: int
    daily_profit_usd: float

    @property
    def total_return_usd(self) -> float:
        return self.duration_days * self.daily_profit_usd


MACHINE_PLANS = [
    MachinePlan("starter", "Starter 50", 50.0, 30, 1.2),
    MachinePlan("pro", "Pro 150", 150.0, 45, 4.3),
    MachinePlan("elite", "Elite 300", 300.0, 60, 9.2),
    MachinePlan("max", "Max 600", 600.0, 75, 20.0),
]
