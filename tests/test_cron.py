from datetime import datetime, timedelta, timezone

import pytest

from scheduler.cron import InvalidCronError, next_fire_time, validate_cron

UTC = timezone.utc


def dt(*args):
    return datetime(*args, tzinfo=UTC)


@pytest.mark.parametrize("expr", ["* * * * *", "0 2 * * *", "*/5 * * * *", "0 0 29 2 *", "0 0 * * mon-fri", "0 0 L * *", "0 0 * * 7"])
def test_valid_expressions_accepted(expr):
    assert validate_cron(expr) == expr


@pytest.mark.parametrize(
    "expr",
    ["", "   ", "* * * *", "* * * * * *", "@daily", "60 * * * *", "0 0 0 0 0", "a b c d e", "0 0 31 2 *", "0 0 31 4 *"],
)
def test_invalid_expressions_rejected(expr):
    with pytest.raises(InvalidCronError):
        validate_cron(expr)


def test_whitespace_is_normalized():
    assert validate_cron("  0   2 *  * * ") == "0 2 * * *"


def test_next_fire_is_strictly_after():
    on_boundary = dt(2026, 1, 1, 0, 0)
    assert next_fire_time("0 0 * * *", on_boundary) == dt(2026, 1, 2, 0, 0)
    assert next_fire_time("* * * * *", on_boundary) == dt(2026, 1, 1, 0, 1)


def test_next_fire_mid_interval():
    assert next_fire_time("*/15 * * * *", dt(2026, 1, 1, 10, 7, 30)) == dt(2026, 1, 1, 10, 15)


def test_month_and_year_rollover():
    assert next_fire_time("0 0 1 * *", dt(2026, 12, 31, 23, 59)) == dt(2027, 1, 1, 0, 0)


def test_leap_day_skips_to_next_leap_year():
    assert next_fire_time("0 0 29 2 *", dt(2026, 3, 1)) == dt(2028, 2, 29, 0, 0)


def test_last_day_of_month():
    assert next_fire_time("0 0 L * *", dt(2026, 2, 1)) == dt(2026, 2, 28, 0, 0)


def test_day_of_week_zero_and_seven_are_sunday():
    sunday = dt(2026, 1, 4)  # a Sunday
    assert next_fire_time("0 0 * * 0", dt(2026, 1, 1)) == sunday
    assert next_fire_time("0 0 * * 7", dt(2026, 1, 1)) == sunday


def test_weekday_range():
    # Fri 2026-01-02 23:00 -> next weekday midnight is Mon 2026-01-05
    assert next_fire_time("0 0 * * mon-fri", dt(2026, 1, 2, 23, 0)) == dt(2026, 1, 5, 0, 0)


def test_non_utc_input_is_converted_and_result_is_utc():
    ist = timezone(timedelta(hours=5, minutes=30))
    after = datetime(2026, 1, 1, 5, 30, tzinfo=ist)  # == 2026-01-01 00:00 UTC
    result = next_fire_time("0 0 * * *", after)
    assert result == dt(2026, 1, 2, 0, 0)
    assert result.utcoffset() == timedelta(0)


def test_naive_datetime_rejected():
    with pytest.raises(ValueError):
        next_fire_time("* * * * *", datetime(2026, 1, 1))


def test_invalid_expression_rejected_by_next_fire_time():
    with pytest.raises(InvalidCronError):
        next_fire_time("not a cron", dt(2026, 1, 1))
