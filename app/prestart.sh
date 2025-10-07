#!/usr/bin/env bash

set -e

echo "Start apply migrations.."
alembic upgrade head
echo "Migrations applied!"

exec "$@"