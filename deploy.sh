#!/bin/bash
# GCEでdocker-composeコマンドが使えなかったため、それ用のdocker imageを使用
cd 22zemi
git checkout production
git pull origin production:production
docker run \
--rm -v /var/run/docker.sock:/var/run/docker.sock \
-v "$PWD:/$PWD" -w="/$PWD" \
docker/compose:1.29.2 \
up -d