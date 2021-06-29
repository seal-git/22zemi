#!/bin/bash
# GCEでdocker-composeコマンドが使えなかったため、それ用のdocker imageを使用
cd 22zemi
git checkout production
git add .
git commit -m "update"
git fetch origin
git merge origin/production
docker stop react python-flask mysql

docker run \
--rm -v /var/run/docker.sock:/var/run/docker.sock \
-v "$PWD:/$PWD" -w="/$PWD" \
docker/compose:1.29.2 \
build

docker run \
--rm -v /var/run/docker.sock:/var/run/docker.sock \
-v "$PWD:/$PWD" -w="/$PWD" \
docker/compose:1.29.2 \
up -d