#!/bin/bash

BASE_URL="http://localhost:5050/api"

echo "=== SMOKETEST: BOXING APP ==="

print_status() {
  if [ $1 -eq 0 ]; then
    echo "[PASS] $2"
  else
    echo "[FAIL] $2"
    exit 1
  fi
}

# Health checks
echo "-> Checking service health..."
curl -s "$BASE_URL/health" | grep -q '"status": "success"'
print_status $? "Health check passed"

echo "-> Checking database connection..."
curl -s "$BASE_URL/db-check" | grep -q '"status": "success"'
print_status $? "Database check passed"

# Clear previous state
echo "-> Clearing ring and resetting DB..."
curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

# Add Boxer 1
echo "-> Creating Boxer1..."
curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d '{
  "name": "SmokeyOne",
  "weight": 180,
  "height": 70,
  "reach": 72.5,
  "age": 28
}' | grep -q '"status": "success"'
print_status $? "Boxer1 created"

# Add Boxer 2
echo "-> Creating Boxer2..."
curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d '{
  "name": "SmokeyTwo",
  "weight": 190,
  "height": 72,
  "reach": 74.0,
  "age": 30
}' | grep -q '"status": "success"'
print_status $? "Boxer2 created"

# Error: Try duplicate
echo "-> Trying to create duplicate Boxer1..."
curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d '{
  "name": "SmokeyOne",
  "weight": 180,
  "height": 70,
  "reach": 72.5,
  "age": 28
}' | grep -q "already exists"
print_status $? "Duplicate boxer rejected"

# Enter ring
echo "-> Entering Boxer1 into ring..."
curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d '{"name": "SmokeyOne"}' | grep -q '"status": "success"'
print_status $? "Boxer1 entered ring"

echo "-> Entering Boxer2 into ring..."
curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d '{"name": "SmokeyTwo"}' | grep -q '"status": "success"'
print_status $? "Boxer2 entered ring"

# Error: Add third boxer and try to enter (should fail)
echo "-> Creating Boxer3..."
curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d '{
  "name": "SmokeyThree",
  "weight": 170,
  "height": 68,
  "reach": 71.0,
  "age": 26
}' > /dev/null

echo "-> Trying to enter Boxer3 (should fail)..."
curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d '{"name": "SmokeyThree"}' | grep -q "Ring is full"
print_status $? "Third boxer rejected correctly"

# Fight!
echo "-> Simulating fight..."
curl -s "$BASE_URL/fight" | grep -q '"winner":'
print_status $? "Fight completed"

# Leaderboard
echo "-> Checking leaderboard..."
curl -s "$BASE_URL/leaderboard" | grep -q '"status": "success"'
print_status $? "Leaderboard retrieved"

echo "ALL SMOKETESTS PASSED SUCCESSFULLY!"


