from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from scheduler.core.db import engine
from scheduler.models import JobDefinition, JobRun

FIRE_TIME = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)


def make_job(db, name="nightly_report"):
    job = JobDefinition(name=name, cron_expression="0 2 * * *")
    db.add(job)
    db.commit()
    return job


def test_job_definition_defaults(db):
    job = make_job(db)
    db.refresh(job)
    assert job.id is not None
    assert job.is_active is True
    assert job.catch_up_policy == "SKIP"
    assert job.max_retries == 3
    assert job.payload is None
    assert job.next_run_time is None
    assert job.created_at is not None


def test_job_run_defaults(db):
    job = make_job(db)
    run = JobRun(job_id=job.id, scheduled_for=FIRE_TIME, status="PENDING")
    db.add(run)
    db.commit()
    db.refresh(run)
    assert run.attempt == 1
    assert run.started_at is None and run.completed_at is None and run.error_message is None


def test_payload_roundtrips_as_jsonb(db):
    job = JobDefinition(name="p", cron_expression="* * * * *", payload={"a": [1, 2], "b": {"c": True}})
    db.add(job)
    db.commit()
    db.expire_all()
    assert db.get(JobDefinition, job.id).payload == {"a": [1, 2], "b": {"c": True}}


def test_duplicate_job_and_scheduled_for_is_rejected(db):
    job = make_job(db)
    db.add(JobRun(job_id=job.id, scheduled_for=FIRE_TIME, status="PENDING"))
    db.commit()
    db.add(JobRun(job_id=job.id, scheduled_for=FIRE_TIME, status="PENDING"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_same_scheduled_for_allowed_for_different_jobs(db):
    a, b = make_job(db, "a"), make_job(db, "b")
    db.add_all([
        JobRun(job_id=a.id, scheduled_for=FIRE_TIME, status="PENDING"),
        JobRun(job_id=b.id, scheduled_for=FIRE_TIME, status="PENDING"),
    ])
    db.commit()


def test_job_run_requires_existing_job(db):
    import uuid

    db.add(JobRun(job_id=uuid.uuid4(), scheduled_for=FIRE_TIME, status="PENDING"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_status_index_exists():
    indexes = {i["name"]: i["column_names"] for i in inspect(engine).get_indexes("job_runs")}
    assert indexes["idx_job_runs_status"] == ["status", "scheduled_for"]
