python-flask/app
===================

# ファイル
database_setting.py: データベースの構成と接続をする．
database_functions.py: データベース関連の関数を置く．
models.py: flaskがhttpクエリを受け取る．
recommend.py: 表示順を決定する．
api_functions: APIへアクセスして情報を取得する
calc_info.py: api_functionsで使う関数を置く．投票数やオススメ度など，レスポンスする情報を計算する。

# 主な流れ
invite: 
	models.py/https_invite()
		→ recommend.py/recommend_main()
			→ recommend.py/pre_info()
			→ api_functions.py/search_restaurants_info()
				⇄ calc_info.py
			→ recommend.py/response_info()
			→ api_functions.py/get_restaurants_info()
				⇄ calc_info.py

feeling: 
	models.py/https_feeling()

list:
	models.py/https_list()
		→ api_functions.py/get_restaurants_info()
				⇄ calc_info.py

