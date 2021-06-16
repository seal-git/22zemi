# 飯Tinder(仮称)
## 起動方法
docker-compose.ymlのあるディレクトリで

```
docker compose build
docker compose up -d
```
localhost:3000でアプリにアクセスできる．

起動すると，次のポートが開く．
- react 
  - 3000
- python-flask
  - 5000
- mysql
  - 3306

## コンテナ内に入りたい場合
```
docker exec -it react bash
```
`react`を`python-flask` `mysql`にすればそれぞれのコンテナに入って作業できる．
