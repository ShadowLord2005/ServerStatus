#!/bin/bash

echo "Starting Init Script"

if test -f "./run.pid"; then
    echo "PID exists, Killing previous Bot"
    cat run.pid | xargs kill
fi

cd ServerStatus || exit 1

echo "ServerStatus Folder Exists, running git pull"

git pull

"/home/${USER}/.local/bin/uv" sync

echo "Repo Pulled and .venv synced"

nohup "/home/${USER}/.local/bin/uv" run -qq --env-file .env serverstatus & echo $! > run.pid

echo "Bot Logged in and Running"

exit 0