from datetime import datetime, timezone

from croniter import CroniterBadDateError, croniter

CRON_FIELDS = 5


class InvalidCronError(ValueError):
    pass


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


def validate_cron(expression: str) -> str:
    """Return the normalized expression, or raise InvalidCronError.

    Only standard 5-field cron is accepted. croniter also accepts 6-field
    (seconds) expressions and @aliases, which are out of scope for the poller.
    """
    fields = expression.split()
    if len(fields) != CRON_FIELDS:
        raise InvalidCronError(f"cron expression must have exactly {CRON_FIELDS} fields")
    normalized = " ".join(fields)
    if not croniter.is_valid(normalized):
        raise InvalidCronError(f"invalid cron expression: {normalized!r}")
    # Syntactically valid expressions like "0 0 31 2 *" can never fire.
    try:
        croniter(normalized, datetime(2026, 1, 1, tzinfo=timezone.utc)).get_next(datetime)
    except CroniterBadDateError:
        raise InvalidCronError(f"cron expression never fires: {normalized!r}") from None
    return normalized


def next_fire_time(expression: str, after: datetime) -> datetime:
    """First fire time strictly after `after`, evaluated in UTC."""
    after = _to_utc(after)
    return croniter(validate_cron(expression), after).get_next(datetime)
