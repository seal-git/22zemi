# Reskima

## 本番環境
* https://reskima.com
* IP: 34.146.106.163
* productionブランチに何かがpushされたらgithub actionsの自動デプロイが走る
* **デプロイされてから最大10分ほど経たないとサイトにはアクセスできないので注意**
* VMインスタンス内で直接docker-composeするときはrootでやらないとエラーになる
* .envファイルはサーバー内で直接編集する
## 環境構築の方法
1. (ローカルで)**origin/mainからこのブランチにマージ**
2. productionブランチとしてpush
3. 本番環境で自動ビルドが走る



