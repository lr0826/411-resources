# Use an official Python runtime
FROM python:3.9-slim

# Set working dir
WORKDIR /app

# Copy all local files into container
COPY . /app

# Copy .env
COPY .env /app/.env

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite
RUN apt-get update && apt-get install -y sqlite3

# Make sure the DB scripts are executable
RUN chmod +x /app/sql/create_db.sh

# Expose port 5000
EXPOSE 5000

# For debugging: show what's in /app
# RUN ls -l /app && ls -l /app/sql

# Run your entrypoint script (assuming it calls create_db.sh and ends with flask run)
CMD ["/app/entrypoint.sh"]

