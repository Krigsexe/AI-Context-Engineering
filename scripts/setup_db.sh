#!/bin/bash
# =============================================================================
# ODIN v7.0 - Database Setup Script
# =============================================================================
set -e

echo "Setting up database..."

# Wait for PostgreSQL
until docker exec odin-postgres pg_isready -U ${POSTGRES_USER:-odin} > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo "PostgreSQL is ready."

# Run migrations
for migration in database/migrations/*.sql; do
    if [ -f "$migration" ]; then
        echo "Running migration: $migration"
        docker exec -i odin-postgres psql -U ${POSTGRES_USER:-odin} -d ${POSTGRES_DB:-odin} < "$migration"
    fi
done

echo "Database setup complete."
