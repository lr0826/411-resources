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
result=$?
if [ $result -eq 0 ]; then
  print_status $result "Health check passed"
else
  print_status $result "Health check failed"
fi

echo "-> Checking database connection..."
curl -s "$BASE_URL/db-check" | grep -q '"status": "success"'
result=$?
if [ $result -eq 0 ]; then
  print_status $result "Database check passed"
else
  print_status $result "Database check failed"
fi

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

# Clear previous state again
echo "-> Clearing ring and resetting DB..."
curl -s -X POST "$BASE_URL/clear-boxers" > /dev/null

# Ask user for custom boxers
read -p "Do you want to create custom boxers? (y/n): " CREATE_CUSTOM

if [[ "$CREATE_CUSTOM" =~ ^[Yy]$ ]]; then
  echo "-> Creating custom boxer 1..."
  read -p "Enter name: " BOXER1_NAME
  read -p "Enter weight: " BOXER1_WEIGHT
  read -p "Enter height: " BOXER1_HEIGHT
  read -p "Enter reach: " BOXER1_REACH
  read -p "Enter age: " BOXER1_AGE

  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d "{
    \"name\": \"$BOXER1_NAME\",
    \"weight\": $BOXER1_WEIGHT,
    \"height\": $BOXER1_HEIGHT,
    \"reach\": $BOXER1_REACH,
    \"age\": $BOXER1_AGE
  }" | grep -q '"status": "success"'
  print_status $? "Custom boxer ($BOXER1_NAME) created"

  echo "-> Creating custom boxer 2..."
  read -p "Enter name: " BOXER2_NAME
  read -p "Enter weight: " BOXER2_WEIGHT
  read -p "Enter height: " BOXER2_HEIGHT
  read -p "Enter reach: " BOXER2_REACH
  read -p "Enter age: " BOXER2_AGE

  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" -d "{
    \"name\": \"$BOXER2_NAME\",
    \"weight\": $BOXER2_WEIGHT,
    \"height\": $BOXER2_HEIGHT,
    \"reach\": $BOXER2_REACH,
    \"age\": $BOXER2_AGE
  }" | grep -q '"status": "success"'
  print_status $? "Custom boxer ($BOXER2_NAME) created"

  # Enter ring
  echo "-> Entering $BOXER1_NAME into ring..."
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\": \"$BOXER1_NAME\"}" | grep -q '"status": "success"'
  print_status $? "$BOXER1_NAME entered ring"

  echo "-> Entering $BOXER2_NAME into ring..."
  curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" -d "{\"name\": \"$BOXER2_NAME\"}" | grep -q '"status": "success"'
  print_status $? "$BOXER2_NAME entered ring"

  echo "-> Simulating fight..."
  curl -s "$BASE_URL/fight" | grep -q '"winner":'
  print_status $? "Fight completed"

  echo "-> Checking leaderboard..."
  curl -s "$BASE_URL/leaderboard" | grep -q '"status": "success"'
  print_status $? "Leaderboard retrieved"
else
  echo "Skipping custom boxer creation."
fi

echo "ALL SMOKETESTS PASSED SUCCESSFULLY!"



