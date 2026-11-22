#!/bin/bash

if [ -f /run.pid ]; then
    cat run.pid | xargs kill
fi

cd ServerStatus || exit 1

git pull

"/home/${USER}/.local/bin/uv" sync

nohup "/home/${USER}/.local/bin/uv" run -qq --env-file .env serverstatus & echo $! > run.pid

exit 0