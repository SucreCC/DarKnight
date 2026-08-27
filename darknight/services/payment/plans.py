from dataclasses import dataclass


@dataclass(frozen=True)
class PlanCycle:
    price: float
    data_limit_gb: int
    duration_days: int


# Prices are in the currency configured under `paypal.currency` (USD by default),
# converted from the original CNY list at roughly 7.2 CNY/USD.
PLAN_CATALOG: dict[tuple[str, str], PlanCycle] = {
    ("100g", "yearly"): PlanCycle(price=1.99, data_limit_gb=100, duration_days=365),
    ("100g", "two_years"): PlanCycle(price=2.99, data_limit_gb=100, duration_days=730),
    ("1024g", "quarterly"): PlanCycle(price=2.49, data_limit_gb=1024, duration_days=90),
    ("2048g", "monthly"): PlanCycle(price=0.99, data_limit_gb=2048, duration_days=30),
}


def get_plan_cycle(plan_id: str, cycle_id: str) -> PlanCycle | None:
    return PLAN_CATALOG.get((plan_id, cycle_id))


def group_plan_catalog() -> dict[str, list[tuple[str, PlanCycle]]]:
    """Group the flat catalog by plan, keeping declaration order for display."""
    grouped: dict[str, list[tuple[str, PlanCycle]]] = {}
    for (plan_id, cycle_id), cycle in PLAN_CATALOG.items():
        grouped.setdefault(plan_id, []).append((cycle_id, cycle))
    return grouped


__all__ = ["PLAN_CATALOG", "PlanCycle", "get_plan_cycle", "group_plan_catalog"]
