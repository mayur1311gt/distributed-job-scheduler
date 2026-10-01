# Distributed Job Scheduler with Exactly-Once Execution

A distributed job scheduling system that guarantees exactly-once dispatch of scheduled jobs, built incrementally as a portfolio backend project.

> Portfolio project — built with Claude Code as a pairing tool to deepen system design understanding.

## Stack

- **Language/Framework:** Python, FastAPI
- **Storage:** PostgreSQL
- **Coordination:** Redis (leader election, locking)
- **Messaging:** Kafka (job dispatch/consumption)
- **Deployment:** Docker

MVP tier only — Kubernetes, gRPC, and distributed tracing are explicitly out of scope until a later phase.

## Architecture

_To be filled in as the system is built. See `docs/ARCHITECTURE.md` for a running log of design decisions, alternatives considered, and why they were rejected._

## Build Plan

- **Week 1:** Job CRUD API, Postgres schema, single-instance cron polling loop, basic worker
- **Week 2:** Redis leader election, Kafka dispatch/consumption, per-run lock, retry/backoff
- **Week 3:** Dead-letter handling, catch-up policy, structured logging, metrics, Dockerize, CI with a race-condition integration test proving exactly-once dispatch
- **Week 4:** Cloud deployment, Grafana dashboard, architecture README, demo video
- **Later (stretch):** service split, gRPC, EKS, tracing
