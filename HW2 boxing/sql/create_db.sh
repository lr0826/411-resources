#!/bin/bash

DB_PATH=/app/db/boxing.db

if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    sqlite3 "$DB_PATH" < /app/db/init_db.sql
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    sqlite3 "$DB_PATH" < /app/db/init_db.sql
    echo "Database created successfully."
fi
