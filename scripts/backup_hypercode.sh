#!/bin/bash
DATE=$(date +%Y-%m-%d_%H_%M_%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

echo "Backing up Postgres Database..."
docker exec -t postgres pg_dumpall -c -U postgres > "$BACKUP_DIR/hypercode_db_$DATE.sql"

if [ $? -eq 0 ]; then
    echo -e "\033[0;32mDatabase backup successful: $BACKUP_DIR/hypercode_db_$DATE.sql\033[0m"
else
    echo -e "\033[0;31mDatabase backup failed!\033[0m"
fi
