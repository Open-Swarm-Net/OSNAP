#!/bin/bash

# Define the specific docker-compose files
COMPOSE_FILE1="docker-compose.receiver.yml"
COMPOSE_FILE2="docker-compose.sender.yml"

docker-compose -f "$COMPOSE_FILE1" -f "$COMPOSE_FILE2" up --build