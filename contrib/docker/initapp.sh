#!/bin/bash

cat > /app/userapi.conf <<EOF
HOST = "0.0.0.0"
SQLALCHEMY_DATABASE_URI = "sqlite:////app/userapi.db"
EOF

if [ ! -e /app/userapi.db ]; then
    python /app/manage.py -c /app/userapi.conf create_db
fi

pushd /app
python ./manage.py -c /app/userapi.conf runserver -h 0.0.0.0
