#!/bin/bash

echo "Starting Init Script"

cd ServerStatus || exit 1

if test -f "./run.pid"; then
    echo "PID exists, Killing previous Bot"
    cat run.pid | xargs kill -15
    mv "nohup.out" "nohup_$(date +%Y-%m-%d_%H-%M-%S).out"
fi

echo "Running Git Pull"

git pull

"/home/${USER}/.local/bin/uv" sync

echo "Repo Pulled and .venv synced"

nohup "/home/${USER}/.local/bin/uv" run -qq --env-file .env serverstatus & echo $! > run.pid

echo "Bot Logged in and Running"

exit 0