#!/usr/bin/env bash
set -e

docker-compose exec -T postgres psql -U gmgn -d gmgn_research < sql/schema.sql
