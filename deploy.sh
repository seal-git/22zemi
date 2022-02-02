#!/bin/bash
# GCEでdocker-composeコマンドが使えなかったため,それ用のdocker imageを使用
docker stop react python-flask mysql https
cd 22zemi
git checkout production
git fetch origin
git reset --hard origin/production

docker-compose build
docker-compose up