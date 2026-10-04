"""Date parsing and reporting-period helpers."""

from datetime import date


def parse_iso_date(value: date | str) -> date:
    """Return a date from an ISO string or pass through an existing date."""
    return value if isinstance(value, date) else date.fromisoformat(value)


def month_bounds(value: date | str) -> tuple[date, date]:
    """Return the first and last date of the containing calendar month."""
    current = parse_iso_date(value)
    if current.month == 12:
        next_month = date(current.year + 1, 1, 1)
    else:
        next_month = date(current.year, current.month + 1, 1)
    return date(current.year, current.month, 1), date.fromordinal(next_month.toordinal() - 1)
