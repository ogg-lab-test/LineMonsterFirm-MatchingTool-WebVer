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
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# 外部ライブラリ
import pandas as pd
# import psutil
# from memory_profiler import profile

# 自作ライブラリ等
from lib.classes import DataList
from lib.classes import SessionDataList
from lib.process_event import entry_set_th
from lib.process_event import entry_set_th_from_cmb
from lib.process_event import select_set_ops
from lib.process_event import reset_select_box
from lib.process_event import button_calc_affinity
from lib.process_log import print_log



# ページの初期設定
def init_page_setting(web_title, title, version):

    # ページ設定
    st.set_page_config(page_title=web_title, layout="wide", initial_sidebar_state="expanded")

    # 見出しのリンクを削除
    delete_link()

    # タイトル
    st.title(title)
    st.write(version)

    return



def delete_link():

    # 見出しについてしまうリンクを削除
    st.html(
        body="""
            <style>
                /* hide hyperlink anchors generated next to headers */
                h1 > div > a {
                    display: none !important;
                }
                h2 > div > a {
                    display: none !important;
                }
                h3 > div > a {
                    display: none !important;
                }
                h4 > div > a {
                    display: none !important;
                }
                h5 > div > a {
                    display: none !important;
                }
                h6 > div > a {
                    display: none !important;
                }
            </style>
        """,
    )

    return



# セッション系の初期化
def init_session_state(datalist):

    # 個別保存領域の初期化
    if "session_datalist" not in st.session_state:
        st.session_state.session_datalist = SessionDataList()
        # セレクトボックスの絞込み用のDataFrame型を用意。
        st.session_state.session_datalist.df_monsters_c = datalist.df_monsters
        st.session_state.session_datalist.df_monsters_pg = datalist.df_monsters

    ### ラジオボタンの選択結果保存領域作成(★ラジオボタンの選択結果は先頭1文字を使用して判別しているため注意。)
    # 計算式設定
    if "radio_calc_list" not in st.session_state:
        st.session_state.radio_calc_list = ["1.min(m)式", "2.min(m+s)式"]
    
    if "radio_calc" not in st.session_state:
        st.session_state.radio_calc = st.session_state.radio_calc_list[1]

    # 参照テーブル設定
    if "radio_table_list" not in st.session_state:
        st.session_state.radio_table_list = ["1.純血統+レア", "2.全モンスター", "3.全モンスター(純血統のみ除く)"]

    if "radio_c" not in st.session_state:
        st.session_state.radio_c = st.session_state.radio_table_list[1]
    if "radio_pg" not in st.session_state:
        st.session_state.radio_pg = st.session_state.radio_table_list[1]
    if "radio_c_prev" not in st.session_state:
        st.session_state.radio_c_prev = st.session_state.radio_table_list[1]
    if "radio_pg_prev" not in st.session_state:
        st.session_state.radio_pg_prev = st.session_state.radio_table_list[1]

    # セレクトボックス選択結果保存域作成
    for i in range(DataList.num_monster):
        if f"select_ops_name{i}" not in st.session_state:
            st.session_state[f"select_ops_name{i}"] = ""
        elif f"select_ops_main{i}" not in st.session_state:
            st.session_state[f"select_ops_main{i}"] = ""
        elif f"select_ops_sub{i}" not in st.session_state:
            st.session_state[f"select_ops_sub{i}"] = ""

    # 全セレクトボックスの初期リスト設定
    if "select_options" not in st.session_state:
        st.session_state.select_options = [ [ 0 for j in range(DataList.num_monster) ] for i in range(DataList.num_kind)]
        for i in range(DataList.num_monster):
            st.session_state.select_options[0][i] = datalist.lis_mons_names
            st.session_state.select_options[1][i] = datalist.lis_main_ped
            st.session_state.select_options[2][i] = datalist.lis_sub_ped

    # 閾値設定箇所の有効/無効化フラグ
    if f"input_threshs_disabled" not in st.session_state:
        st.session_state.input_threshs_disabled = [False] * DataList.num_threshs

    # 閾値関連の領域初期化
    for i in range(DataList.num_threshs):
        if f"input_thresh{i}" not in st.session_state:
            st.session_state[f"input_thresh{i}"] = 0
    if f"input_thresh" not in st.session_state:
       st.session_state.input_thresh = True
       entry_set_th()

    # 1回以上検索しているかどうかのフラグ
    if f"is_search_once_more" not in st.session_state:
        st.session_state.is_search_once_more = False

    return



# ラジオボタン作成関数
def create_radio_button(datalist):

    # 表示
    st.write('')
    st.header('モンスター参照テーブル', help="子/親祖父母毎に検索で使用するテーブルを設定します。変更時、関連するモンスター名設定をクリアし、閾値を再設定します。")
    
    # テーブル選択結果格納場所の初期化
    st.session_state.session_datalist.lis_choice_table = [int(st.session_state.radio_c[0]), int(st.session_state.radio_pg[0])]
    
    # ラジオボタン作成
    c  = st.radio("子",      st.session_state.radio_table_list, horizontal=True, key="radio_c", on_change=reset_select_box, args=(datalist, False, True, False, ), help="検索時に使用する子のモンスター名テーブルを設定します。設定内容に合わせて閾値を自動調整します。")
    pg = st.radio("親祖父母", st.session_state.radio_table_list, horizontal=True, key="radio_pg", on_change=reset_select_box, args=(datalist, False, False, True, ), help="検索時に使用する親祖父母のモンスター名テーブルを設定します。設定内容に合わせて閾値を自動調整します。")

    # 値設定
    st.session_state.session_datalist.lis_choice_table[0] = int(c[0])
    st.session_state.session_datalist.lis_choice_table[1] = int(pg[0])

    return



# リセット/セレクトボックスの作成
def create_select_area(datalist):

    # 表示
    st.write('')
    st.header('モンスター名設定', help="ここで検索したいモンスターの設定をします。全て空白でも検索可能ですが、相性値閾値設定次第で候補過多で出力されなくなるため注意。(メイン/サブ血統欄はモンスター名絞込み用の設定です。）")
    
    # リセットボタンの作成(押下でリセット＆セレクトボックス作成、)
    if st.button('モンスター名選択リセット', help="選択済みのセレクトボックスの内容と閾値を初期化します。"):
        reset_select_box(datalist)
    
    # セレクトボックスの作成
    create_select_box(datalist)



# セレクトボックス作成関数
def create_select_box(datalist):
    
    # ラベルの初期化
    lis_s_ops_labels = ['子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']

    # セレクトボックス作成
    for i in range(DataList.num_monster):
        col1, col2, col3 = st.columns(DataList.num_kind)
        with col1:
            st.session_state.session_datalist.lis_names[0][i] = st.selectbox(lis_s_ops_labels[i], st.session_state.select_options[0][i], index = 0, key=f'select_ops_name{i}', on_change=entry_set_th_from_cmb, args=(datalist, ), help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
        with col2:
            st.session_state.session_datalist.lis_names[1][i] = st.selectbox('メイン血統',         st.session_state.select_options[1][i], index = 0, key=f'select_ops_main{i}', on_change=select_set_ops, args=(datalist, i), help="モンスターのメイン血統を設定します。(絞込み用のため、不要なら設定不要。)")
        with col3:
            st.session_state.session_datalist.lis_names[2][i] = st.selectbox('サブ血統',           st.session_state.select_options[2][i], index = 0, key=f'select_ops_sub{i}', on_change=select_set_ops, args=(datalist, i), help="モンスターのメイン血統を設定します。(絞込み用のため、不要なら設定不要。)")
    
    return



# 詳細設定欄の作成
def create_details(datalist):

    # 表示
    st.write('')
    st.header('詳細設定')
    if st.checkbox("詳細に設定したい場合はチェックをつけてください。"):
        
        # 計算式選択ボタンの作成
        create_radio_button_exp(datalist)

        # 入力エリアの作成
        create_number_input(datalist)
    
    else:
        # 初期閾値を更新しておく
        for i in range(DataList.num_threshs):
            datalist.lis_threshs[i] = st.session_state[f"input_thresh{i}"]
        
    return



# 計算式指定ラジオボタン作成
def create_radio_button_exp(datalist):

    # 表示
    st.write('')
    st.subheader('計算式', help="相性値を計算する際の計算式を指定します。")

    # ラジオボタン作成
    choice  = st.radio("計算手法",      st.session_state.radio_calc_list, horizontal=True, key="radio_calc", index=1, on_change=entry_set_th_from_cmb, args=(datalist, ), help="相性値を計算する際の計算式を指定します。")

    return



# 閾値入力エリア作成
def create_number_input(datalist):

    # 表示
    st.write('')
    st.subheader('相性値閾値設定', help="本項目での設定値未満の相性値の場合、検索候補から除外します。（よくわからない場合はそのままで問題なし。）")

    # ラベルを作成
    label_names = ["a.子-親-祖父-祖母メイン血統の相性値閾値", "b.子-親-祖父-祖母サブ血統の相性値閾値", 
                    "c.親①-親②メイン血統の相性値閾値", "d.親①-親②サブ血統の相性値閾値", 
                    "e.子-親①間のメイン/サブ血統相性値合計閾値", "f.子-親②間のメイン/サブ血統相性値合計閾値",
                    "g.親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値", 
                    "h.親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値"]
    
    # テキスト入力エリアを設定
    for i in range(len(label_names)):
        st.number_input(label_names[i], min_value=0, value=datalist.lis_threshs[i], key=f"input_thresh{i}", disabled=st.session_state.input_threshs_disabled[i])

    return



# 検索ボタンの作成
def create_search_button(datalist, used_memory):

    # 表示
    st.write('')
    st.header('検索')

    # 検索ボタン作成(ボタン押下で検索開始)
    if st.button('検索開始！'):
        if used_memory < DataList.max_memory_size:
            with st.spinner('processiong...'):
                # 検索
                ret = button_calc_affinity(datalist)
        else:
            st.warning("現在、他のユーザが使用中です。しばらく時間を空けて再度お試しください。なお、しばらくたっても状態が変わらない場合は、管理者にお問い合わせください。")
    
    return



# 結果の表示
def disp_result(used_memory):

    # 表示
    st.write('')
    st.header('検索結果', help="「検索開始！」ボタン押下後に設定値および結果が出力されます。なお、結果は最大5,000件までとなります。")
    st.write(f"現在のメモリ使用量: {used_memory:.2f} MB")

    # 1回以上検索実施されている場合のみ結果等を表示
    if st.session_state.is_search_once_more:
        
        # 設定値の表示
        print_log()

        # 結果の表示
        with st.spinner('processiong...'):
            
            # 結果1件以上で表示
            if len(st.session_state.session_datalist.df_affinities.index) >= 1:

                # st.dataframe(st.session_state.session_datalist.df_affinities, width=2000, height=500, use_container_width=True)

                gb = GridOptionsBuilder.from_dataframe(st.session_state.session_datalist.df_affinities)
                gb.configure_selection(selection_mode="multiple", use_checkbox=True)
                gridOptions = gb.build()
                row = AgGrid(st.session_state.session_datalist.df_affinities, 
                    gridOptions=gridOptions, 
                    enable_enterprise_modules=True, 
                    allow_unsafe_jscode=True, 
                    update_mode=GridUpdateMode.SELECTION_CHANGED)

    else:
        pass

    return


