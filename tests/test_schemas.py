import pytest
from pydantic import ValidationError

from scheduler.schemas import JobCreate


def test_defaults():
    job = JobCreate(name="nightly_report", cron_expression="0 2 * * *")
    assert job.catch_up_policy == "SKIP"
    assert job.max_retries == 3
    assert job.payload is None


def test_name_and_cron_are_normalized():
    job = JobCreate(name="  report  ", cron_expression=" 0  2 * * * ")
    assert job.name == "report"
    assert job.cron_expression == "0 2 * * *"


@pytest.mark.parametrize("cron", ["", "* * * *", "@daily", "0 0 31 2 *", "99 * * * *", "x" * 101])
def test_malformed_cron_rejected(cron):
    with pytest.raises(ValidationError):
        JobCreate(name="j", cron_expression=cron)


@pytest.mark.parametrize("name", ["", "   ", "x" * 256])
def test_bad_name_rejected(name):
    with pytest.raises(ValidationError):
        JobCreate(name=name, cron_expression="* * * * *")


def test_unknown_catch_up_policy_rejected():
    with pytest.raises(ValidationError):
        JobCreate(name="j", cron_expression="* * * * *", catch_up_policy="MAYBE")


@pytest.mark.parametrize("retries", [-1, 11])
def test_max_retries_bounds(retries):
    with pytest.raises(ValidationError):
        JobCreate(name="j", cron_expression="* * * * *", max_retries=retries)


def test_payload_must_be_object():
    with pytest.raises(ValidationError):
        JobCreate(name="j", cron_expression="* * * * *", payload=[1, 2])
