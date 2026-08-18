#!/bin/bash

export PORT=${PORT:-8080}

envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf

python3 /app/app.py &

nginx -g "daemon off;"
