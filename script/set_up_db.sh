#!/bin/bash
DB_NAME='tech_for_all_db'
DB_USER='super_user_tech'
DB_PASS='12345678'
sudo -u postgres psql -c "CREATE USER $DB_USER WITH SUPERUSER PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
echo "Database and user created successfully".