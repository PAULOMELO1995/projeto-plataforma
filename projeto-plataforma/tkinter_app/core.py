from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .constants import MACHINE_PLANS, MIN_WITHDRAW_USD, PLATFORM_RATE_BRL, MachinePlan
from .utils import brl_to_platform_usd, full_days_since, platform_usd_to_brl


@dataclass
class Contract:
    id: str
    plan_id: str
    plan_name: str
    contract_value_usd: float
    duration_days: int
    daily_profit_usd: float
    days_paid: int
    start_date: datetime
    end_date: datetime
    last_payout_date: datetime
    status: str


@dataclass
class Transaction:
    id: str
    type: str
    amount_usd: float
    created_at: datetime
    description: str


class PlatformState:
    def __init__(self) -> None:
        self.user: Optional[dict[str, str]] = None
        self.wallet_usd = 0.0
        self.contracts: list[Contract] = []
        self.transactions: list[Transaction] = []

    def sign_in(self, name: str, email: str) -> None:
        self.user = {"name": name, "email": email}
        self.apply_daily_earnings()

    def get_plan_by_id(self, plan_id: str) -> Optional[MachinePlan]:
        for plan in MACHINE_PLANS:
            if plan.id == plan_id:
                return plan
        return None

    def add_deposit_brl(self, amount_brl: float) -> None:
        amount_usd = brl_to_platform_usd(amount_brl, PLATFORM_RATE_BRL)
        self.wallet_usd += amount_usd
        self.transactions.insert(
            0,
            Transaction(
                id=f"dep-{datetime.now().timestamp()}",
                type="deposit",
                amount_usd=amount_usd,
                created_at=datetime.now(),
                description=f"Depósito confirmado em BRL ({amount_brl:.2f})",
            ),
        )

    def apply_daily_earnings(self) -> float:
        total_credit = 0.0

        for contract in self.contracts:
            if contract.status != "active":
                continue

            elapsed_days = full_days_since(contract.last_payout_date)
            remaining_days = contract.duration_days - contract.days_paid
            payout_days = min(elapsed_days, remaining_days)

            if payout_days <= 0:
                continue

            credit = payout_days * contract.daily_profit_usd
            total_credit += credit

            contract.days_paid += payout_days
            contract.last_payout_date += timedelta(days=payout_days)
            if contract.days_paid >= contract.duration_days:
                contract.status = "completed"

        if total_credit > 0:
            self.wallet_usd += total_credit
            self.transactions.insert(
                0,
                Transaction(
                    id=f"earn-{datetime.now().timestamp()}",
                    type="earnings",
                    amount_usd=total_credit,
                    created_at=datetime.now(),
                    description="Crédito automático de rendimentos diários",
                ),
            )

        return total_credit

    def buy_machine(self, plan_id: str) -> tuple[bool, str]:
        plan = self.get_plan_by_id(plan_id)

        if not plan:
            return False, "Plano não encontrado."

        if self.wallet_usd < plan.contract_value_usd:
            return False, "Saldo insuficiente para contratar este plano."

        now = datetime.now()

        self.wallet_usd -= plan.contract_value_usd
        self.contracts.insert(
            0,
            Contract(
                id=f"contract-{now.timestamp()}",
                plan_id=plan.id,
                plan_name=plan.name,
                contract_value_usd=plan.contract_value_usd,
                duration_days=plan.duration_days,
                daily_profit_usd=plan.daily_profit_usd,
                days_paid=0,
                start_date=now,
                end_date=now + timedelta(days=plan.duration_days),
                last_payout_date=now,
                status="active",
            ),
        )

        self.transactions.insert(
            0,
            Transaction(
                id=f"buy-{now.timestamp()}",
                type="machine_purchase",
                amount_usd=-plan.contract_value_usd,
                created_at=now,
                description=f"Contratação da máquina {plan.name}",
            ),
        )

        return True, "Máquina ativada com sucesso."

    def request_withdraw_usd(self, amount_usd: float) -> tuple[bool, str]:
        if amount_usd < MIN_WITHDRAW_USD:
            return False, f"O saque mínimo é de {MIN_WITHDRAW_USD:.2f} USD."

        if amount_usd > self.wallet_usd:
            return False, "Saldo insuficiente para saque."

        self.wallet_usd -= amount_usd
        self.transactions.insert(
            0,
            Transaction(
                id=f"wd-{datetime.now().timestamp()}",
                type="withdraw_request",
                amount_usd=-amount_usd,
                created_at=datetime.now(),
                description=(
                    "Solicitação de saque "
                    f"({platform_usd_to_brl(amount_usd, PLATFORM_RATE_BRL):.2f} BRL estimado)"
                ),
            ),
        )

        return True, "Solicitação de saque enviada para análise."

    @property
    def active_contracts(self) -> list[Contract]:
        return [contract for contract in self.contracts if contract.status == "active"]

    @property
    def total_daily_profit_usd(self) -> float:
        return sum(contract.daily_profit_usd for contract in self.active_contracts)

    @property
    def estimated_portfolio_return_usd(self) -> float:
        return sum(contract.duration_days * contract.daily_profit_usd for contract in self.contracts)
