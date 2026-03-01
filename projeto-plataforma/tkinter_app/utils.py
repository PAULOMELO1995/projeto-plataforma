from datetime import datetime


def brl_to_platform_usd(brl_value: float, rate_brl: float) -> float:
    return brl_value / rate_brl


def platform_usd_to_brl(usd_value: float, rate_brl: float) -> float:
    return usd_value * rate_brl


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_usd(value: float) -> str:
    return f"US$ {value:,.2f}"


def full_days_since(start_date: datetime, now: datetime | None = None) -> int:
    current = now or datetime.now()
    start_day = start_date.date()
    current_day = current.date()
    delta = current_day - start_day
    return max(0, delta.days)


def format_datetime_br(value: datetime) -> str:
    return value.strftime("%d/%m/%Y %H:%M")
