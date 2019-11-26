#!/bin/bash

echo "stop this application, exec kill <pid>."
echo "check th pid of main.py with pgrep, please make sure you can stop it."

user=`whoami`
pid=`pgrep -u ${user} -f main.py`

if [ -z ${pid} ]; then
  echo "main.py is not running."
  exit 0
fi

read -p "${pid} - kill this pid? (y/n): " yn
case "$yn" in
  [yY]*)
    kill ${pid}
    ;;
  *)
    echo "abort."
    exit 0
    ;;
esac
