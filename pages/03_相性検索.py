"""
   Copyright 2024/6/23 sean of copyright owner

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

	端的に言えば、改変/二次配布は自由ですが、一切責任は負いません！
	配布時は、必ず"sean"の名前と上記文章をコピーして渡すように！って感じです！
	(改変時は面倒ではありますが変更履歴/内容も記載してください。)

"""

# 外部ライブラリ
import psutil
# from memory_profiler import profile

# 自作ライブラリ等
from lib.process_data import init_datalist_for_all_client
from lib.arrange_widget import init_page_setting
from lib.arrange_widget import init_session_state
from lib.arrange_widget import create_radio_button
from lib.arrange_widget import create_select_area
from lib.arrange_widget import create_details
from lib.arrange_widget import create_search_button
from lib.arrange_widget import disp_result



# @profile()
def main():

    # ページの初期設定
    init_page_setting("S Tool", "S Tool", "Version 3.2.0")

    # データリストの初期化
    datalist = init_datalist_for_all_client()

    # セッション初期化
    init_session_state(datalist)

    # リセット/セレクトボックスの作成
    create_select_area(datalist)

    # 詳細設定欄の作成
    create_details(datalist)

    # サーバ全体での現在のメモリ使用量をバイト単位で取得し、MBに変換
    used_memory = psutil.Process().memory_info().rss / (1024 * 1024)

    # 検索
    create_search_button(datalist, used_memory)
    
    # 結果の表示
    disp_result(datalist, used_memory)



# 呼び出し
if __name__ == '__main__':
    main()

