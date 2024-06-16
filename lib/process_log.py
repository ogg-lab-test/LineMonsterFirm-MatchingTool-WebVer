"""
   Copyright 2024/6/2 sean of copyright owner

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

# streamlit関連
import streamlit as st

# 外部ライブラリ
# import psutil
# from memory_profiler import profile

# 自作ライブラリ等
from lib.classes import DataList
# from lib.classes import Monster
# from lib.classes import ThreshAff
# from lib.classes import SessionDataList



# ログ情報の初期化
def init_log():

    st.session_state.log = ""

    return



# ログ領域への書き込み実施
def write_log(message):

    # 保存域の初期化
    if "log" not in st.session_state:
        st.session_state.log = ""
    
    # メッセージに追加
    st.session_state.log += message + "\n"

    return



# 検索時に使用した各種値をログに出力する。
def set_log(Monster_info, thresh_aff):

    message_list1 = ["", '純血統+レア','全モンスター', '全モンスター(純血統のみ除く)']
    message_list2 = ["　　　　子", "　　　親①", "　　祖父①", "　　祖母①", "　　　親②", "　　祖父②", "　　祖母②"]

    # 参照テーブル
    write_log(f"◎モンスター参照テーブル：")
    write_log(f"　　　　　子：{message_list1[st.session_state.session_datalist.lis_choice_table[0]]}")
    write_log(f"　　親祖父母：{message_list1[st.session_state.session_datalist.lis_choice_table[1]]}")

    # 指定モンスター★フォーマットの見直しが必要★
    write_log(f"◎モンスター名：")
    for i, monster in enumerate(Monster_info):
        if monster.name.startswith("("):
            size2 = 60 - len(monster.name) * 4
        else:
            size2 = 54 - len(monster.name) * 4
        size3 = 36 - len(monster.pedigree1) * 4
        size4 = 36 - len(monster.pedigree2) * 4
        write_log(f"{message_list2[i]}:{monster.name:>{size2}}, メイン：{monster.pedigree1:>{size3}}, サブ：{monster.pedigree2:>{size4}}")

    # message_list2にスペースを入れる前の処理。
    # for i, monster in enumerate(Monster_info):
    #     size1 = 10 - len(message_list2[i])
    #     if monster.name.startswith("("):
    #         size2 = 24 - len(monster.name)
    #     else:
    #         size2 = 22 - len(monster.name)
    #     size3 = 12 - len(monster.pedigree1)
    #     size4 = 12 - len(monster.pedigree2)
    #     write_log(f"{message_list2[i]:>{size1}}:{monster.name:>{size2}}, メイン：{monster.pedigree1:>{size3}}, サブ：{monster.pedigree2:>{size4}}")

    # 計算式
    write_log(f"◎計算式：")
    write_log(f"　　計算式：{st.session_state.radio_calc}")

    # 出力パターン
    write_log(f"◎出力パターン：")
    write_log(f"　　パターン方式：{st.session_state.radio_ptn}")
    message = ""
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
        message += "Z-ABB×BAA, " if st.session_state.check_ptn0 else ""
        message += "Z-ABB×BCC, " if st.session_state.check_ptn1 else ""
        message += "Z-ACC×BCC, " if st.session_state.check_ptn2 else ""
        message += "Z-ABC×BCA, " if st.session_state.check_ptn3 else ""
        if len(message) == 0:
            message = "パターン選択無（何も出力されないため注意。）"
    else:
        message = "無効"
    write_log(f"　　パターン選択：{message}")

    # 閾値
    write_log(f"◎相性値閾値：")
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
        write_log(f"　　★★パターン方式に「2.特定パターン」を選択している場合は閾値自動設定のみ有効。")
    else:
        write_log(f"　　a.子-親-祖父-祖母メイン血統の相性値閾値　　　　　　　　　  ：{thresh_aff.th_ped1_cpg}")
        write_log(f"　　b.子-親-祖父-祖母サブ血統の相性値閾値　　　　　　　　　　  ：{thresh_aff.th_ped2_cpg}")
        write_log(f"　　c.親①-親②メイン血統の相性値閾値　　　　　　　　　　　　 ：{thresh_aff.th_ped1_pp}")
        write_log(f"　　d.親①-親②サブ血統の相性値閾値　　　　　　　　　　　　　 ：{thresh_aff.th_ped2_pp}")
        write_log(f"　　e.子-親①間のメイン/サブ血統相性値合計閾値　　　　　　　　：{thresh_aff.th_p1}")
        write_log(f"　　f.子-親②間のメイン/サブ血統相性値合計閾値　　　　　　　　 ：{thresh_aff.th_p2}")
        write_log(f"　　g.親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{thresh_aff.th_cpg1}")
        write_log(f"　　h.親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{thresh_aff.th_cpg2}")

    return



# ログ領域のWeb上への表示
def print_log():
    
    txt = st.text_area("ログ情報", st.session_state.log, height=700, disabled=True, help="設定情報や検索時の途中経過について出力されます。")

    return



# 自端末へのログの保存
def save_log():
    
    return




