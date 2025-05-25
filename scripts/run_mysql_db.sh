#!/bin/bash

# Setting environment variables
export DB_IP="localhost"
export DB_USER="pupilove_admin"
export DB_PASSWORD="12345"
export DB_NAME="pupilove"
export DB_PORT="5001"
CONTAINER_NAME="pupilove_percona_mysql"
DB_SCHEMA_FILE="scripts/db_schema.sql"
SAMPLE_DATA_SQL_FILE="scripts/sample_data.sql"

# Check if a container with the name $CONTAINER_NAME already exists
if [ $(docker ps -aq -f name=$CONTAINER_NAME) ]; then
  echo "Container $CONTAINER_NAME already exists. Removing it..."
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi

# Start Percona MySQL container
docker run -d \
  --platform linux/amd64 \
  --name $CONTAINER_NAME \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -p $DB_PORT:3306 \
  --cpus="0.8" \
  --memory="2g" \
  --memory-swap="10g" \
  percona:latest

# Wait for the container to start
echo "Waiting for the container to start..."
sleep 120

# Create user and database
docker exec -i $CONTAINER_NAME mysql -uroot -proot_password <<EOF
SET GLOBAL max_connections = 2500;
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF

# Load database schema from db_schema.sql
echo "Loading database schema from file $DB_SCHEMA_FILE..."
docker exec -i $CONTAINER_NAME mysql -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$DB_SCHEMA_FILE"
docker exec -i $CONTAINER_NAME mysql -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$SAMPLE_DATA_SQL_FILE"

echo "User $DB_USER created and database $DB_NAME initialized using schema $DB_SCHEMA_FILE."
