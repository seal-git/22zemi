# 飯Tinder(仮称)
## 起動方法
docker-compose.ymlのあるディレクトリで

```
docker compose build
docker compose up -d
```
開発環境では，アプリの立ち上げをコンテナ内に入って手動でやる必要がある．(他にいいやり方があれば)

localhost:3000でアプリにアクセスできる．

起動すると，次のポートが開く．
- react 
  - 3000
- python-flask
  - 5000
- mysql
  - 3306


