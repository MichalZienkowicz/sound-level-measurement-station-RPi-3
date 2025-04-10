#!/bin/bash

session_name="rms_saver_session"

if tmux has-session -t $session_name 2>/dev/null; then
    echo "$session_name is already running. Kill before rerunning."
    exit 1
fi

tmux new-session -d -s $session_name "python3 /home/michz/Project/rms_saver.py"

echo "Uruchomiono sesję tmux: $session_name"
echo "W celu wyłączenia wpisz: tmux kill-session -t $session_name (sprawdz tmux ls)"
