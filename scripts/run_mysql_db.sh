#!/bin/bash

# Ustawienie zmiennych środowiskowych
export DB_IP="localhost"
export DB_USER="pupilove_admin"
export DB_PASSWORD="12345"
export DB_NAME="pupilove"
export DB_PORT="5001"
export CONTAINER_NAME="pupilove_percona_mysql"

# Sprawdzanie, czy kontener o nazwie $CONTAINER_NAME już istnieje
if [ $(docker ps -aq -f name=$CONTAINER_NAME) ]; then
  echo "Kontener $CONTAINER_NAME istnieje. Usuwam go..."
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi

# Uruchomienie kontenera Percona MySQL
docker run -d \
  --platform linux/amd64 \
  --name $CONTAINER_NAME \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -p $DB_PORT:3306 \
  percona:latest

# Czekanie aż kontener wystartuje
echo "Czekam na uruchomienie kontenera..."
sleep 60

# Tworzenie użytkownika i bazy danych
docker exec -i $CONTAINER_NAME mysql -uroot -proot_password <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
USE $DB_NAME;
CREATE TABLE IF NOT EXISTS test_table (
    column1 VARCHAR(255),
    column2 VARCHAR(255),
    column3 VARCHAR(255)
);
INSERT INTO test_table (column1, column2, column3)
VALUES ('Everything', 'is', 'working');
EOF

echo "Użytkownik $DB_USER stworzony i baza danych $DB_NAME utworzona."
