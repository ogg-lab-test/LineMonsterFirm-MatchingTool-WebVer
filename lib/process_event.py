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

# streamlit関連
import streamlit as st

# 外部ライブラリ
import pandas as pd
# import psutil
# from memory_profiler import profile

# 標準ライブラリ
import datetime
import time
import copy

# 自作ライブラリ等
from lib.classes import Monster
from lib.classes import ThreshAff
from lib.classes import DataList
# from lib.classes import SessionDataList
from lib.process_log import init_log
from lib.process_log import write_log
from lib.process_log import set_log
from lib.calc_data import calc_affinity
from lib.calc_data import calc_affinity_select



## ラジオボタン変更後の処理（子のコンボリスト関連の設定）
def radio_set_c_cmb_th(datalist, is_reset=False):

    # 前回値から変更があったかの確認
    if int(st.session_state.radio_c[0]) != int(st.session_state.radio_c_prev[0]) or is_reset:

        # 前回値に今回設定値を保存
        st.session_state.radio_c_prev = st.session_state.radio_c

        # テーブルの設定
        if int(st.session_state.radio_c[0]) == DataList.choice_table_org:
            st.session_state.select_options[0][0] = datalist.lis_mons_names_org
            st.session_state.session_datalist.df_monsters_c = datalist.df_monsters_org
        elif int(st.session_state.radio_c[0]) == DataList.choice_table_all:
            st.session_state.select_options[0][0] = datalist.lis_mons_names
            st.session_state.session_datalist.df_monsters_c = datalist.df_monsters
        elif int(st.session_state.radio_c[0]) == DataList.choice_table_ex_org:
            st.session_state.select_options[0][0] = datalist.lis_mons_names_ex_org
            st.session_state.session_datalist.df_monsters_c = datalist.df_monsters_ex_org
        
        # 閾値の再設定
        entry_set_th()

    return



## ラジオボタン変更後の処理（親祖父母のコンボリスト関連の設定）
def radio_set_pg_cmb_th(datalist, is_reset=False):

    # 前回値から変更があったかの確認
    if int(st.session_state.radio_pg[0]) != int(st.session_state.radio_pg_prev[0]) or is_reset:

        # 前回値に今回設定値を保存
        st.session_state.radio_pg_prev = st.session_state.radio_pg

        # テーブルの設定
        if int(st.session_state.radio_pg[0]) == DataList.choice_table_org:
            for i in range(DataList.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names_org
            st.session_state.session_datalist.df_monsters_pg = datalist.df_monsters_org
        elif int(st.session_state.radio_pg[0]) == DataList.choice_table_all:
            for i in range(DataList.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names
            st.session_state.session_datalist.df_monsters_pg = datalist.df_monsters
        elif int(st.session_state.radio_pg[0]) == DataList.choice_table_ex_org:
            for i in range(DataList.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names_ex_org
            st.session_state.session_datalist.df_monsters_pg = datalist.df_monsters_ex_org
        
        # 閾値の再設定
        entry_set_th()

    return



# テキストボックスの内容更新
# ★同じような処理で、別の設定にするなら、親関数作って、そこでフラグを分けて、子関数で処理するようにした方が管理しやすそう。以降も同じ。
def entry_set_th():
    flag = int(st.session_state.radio_calc[0])
    if flag == DataList.choice_exp1:
        entry_set_th1()
    elif flag == DataList.choice_exp2:
        entry_set_th2()
    return


# min(m)の場合のテキストボックス内閾値初期化
def entry_set_th1():

    # 入力域の無効化
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:
        for i in range(DataList.num_threshs):
            if i < 4:
                st.session_state.input_threshs_disabled[i] = False
            else:
                st.session_state.input_threshs_disabled[i] = True

    # 閾値自動変更無効化チェック
    if st.session_state.input_threshs_chg_disabled:
        return

    # ラジオボタンの設定値取得、一部先行設定
    c_num = int(st.session_state.radio_c[0])
    pg_num = int(st.session_state.radio_pg[0])

    # ラジオボタンの内容に合わせてテキストボックスの内容を設定
    # 論理設計するともう少し最適化できそうだけど、いったんこれで。
    if c_num == DataList.choice_table_org and pg_num == DataList.choice_table_org:
        st.session_state[f"input_thresh0"] = 112
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 36
        
    elif c_num == DataList.choice_table_org and pg_num == DataList.choice_table_all:
        st.session_state[f"input_thresh0"] = 117
        st.session_state[f"input_thresh1"] = 99
        st.session_state[f"input_thresh2"] = 36
        
    elif c_num == DataList.choice_table_org and pg_num == DataList.choice_table_ex_org:
        st.session_state[f"input_thresh0"] = 115
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 36
        
    elif c_num == DataList.choice_table_all and pg_num == DataList.choice_table_org:
        st.session_state[f"input_thresh0"] = 113
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 35
    
    elif c_num == DataList.choice_table_all and pg_num == DataList.choice_table_all:
        st.session_state[f"input_thresh0"] = 119
        st.session_state[f"input_thresh1"] = 98
        st.session_state[f"input_thresh2"] = 38
        
    elif c_num == DataList.choice_table_all and pg_num == DataList.choice_table_ex_org:
        st.session_state[f"input_thresh0"] = 118
        st.session_state[f"input_thresh1"] = 97
        st.session_state[f"input_thresh2"] = 38
        
    elif c_num == DataList.choice_table_ex_org and pg_num == DataList.choice_table_org:
        st.session_state[f"input_thresh0"] = 112
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 33
        
    elif c_num == DataList.choice_table_ex_org and pg_num == DataList.choice_table_all:
        st.session_state[f"input_thresh0"] = 119
        st.session_state[f"input_thresh1"] = 97
        st.session_state[f"input_thresh2"] = 38
    
    elif c_num == DataList.choice_table_ex_org and pg_num == DataList.choice_table_ex_org:
        st.session_state[f"input_thresh0"] = 117
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 38
    
    st.session_state[f"input_thresh3"] = 32
    st.session_state[f"input_thresh4"] = 0
    st.session_state[f"input_thresh5"] = 0
    st.session_state[f"input_thresh6"] = 0
    st.session_state[f"input_thresh7"] = 0

    return



# min(m+s)の場合のテキストボックス内閾値初期化
def entry_set_th2():

    # 入力域の無効化
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:
        for i in range(DataList.num_threshs):
            if i < 2:
                st.session_state.input_threshs_disabled[i] = True
            else:
                st.session_state.input_threshs_disabled[i] = False

    # 閾値自動変更無効化チェック
    if st.session_state.input_threshs_chg_disabled:
        return

    # 初期値設定
    st.session_state[f"input_thresh0"] = 0
    st.session_state[f"input_thresh1"] = 0
    st.session_state[f"input_thresh2"] = 32
    st.session_state[f"input_thresh3"] = 32
    st.session_state[f"input_thresh4"] = 74
    st.session_state[f"input_thresh5"] = 74
    st.session_state[f"input_thresh6"] = 74
    st.session_state[f"input_thresh7"] = 74

    return



# 出力パターンによって、特定の入力域を無効化する。
def radio_disable_entry_cmb(datalist):

    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:

        # セレクトボックスの有効化
        st.session_state.select_ops_disabled[3] = False
        st.session_state.select_ops_disabled[5] = False
        st.session_state.select_ops_disabled[6] = False       

        # パターンのチェックボックス無効化
        st.session_state.check_ptn_disabled = True

        # 入力域を計算式に合わせて元に戻す
        entry_set_th_from_cmb(datalist)

    elif int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:

        # セレクトボックスの一部無効化
        st.session_state.select_ops_disabled[3] = True
        st.session_state.select_ops_disabled[5] = True
        st.session_state.select_ops_disabled[6] = True

        # パターンのチェックボックス有効化
        st.session_state.check_ptn_disabled = False

        # 入力域の無効化
        for i in range(DataList.num_threshs):
            st.session_state.input_threshs_disabled[i] = True

    return



# モンスター名のセレクトボックス設定後、設定値に応じて相性閾値を変更する。
def entry_set_th_from_cmb(datalist):
    
    flag = int(st.session_state.radio_calc[0])
    if flag == DataList.choice_exp1:
        entry_set_th_from_cmb1(datalist)
    elif flag == DataList.choice_exp2:
        entry_set_th_from_cmb2(datalist)
    
    return



# モンスター名のセレクトボックス設定後、設定値に応じて相性閾値を変更する。
# min(m)の時これ。
def entry_set_th_from_cmb1(datalist):
    
    # 初期値設定
    total = 0
    t_list = []
    is_raremon = False
    num_rare = 0  # レアモンスター用の変数（血統ID）
    entry_set_th1()

    # 閾値自動変更無効化チェック
    if st.session_state.input_threshs_chg_disabled:
        return

    # 設定値のカウント
    for i in range(len(st.session_state.select_options[0])):
        name = st.session_state[f'select_ops_name{i}']
        if name != "":
            total += 1
            df_monster = datalist.df_monsters[datalist.df_monsters["モンスター名"] == name]
            if not df_monster.empty and df_monster.iloc[0, 4] == num_rare:
                is_raremon = True
                break

    # 設定値に応じて、相性閾値を算出
    if total != 0:

        if total >= 5:
            t_list = [1, 1, 1, 1]
        elif total == 4:
            t_list = [96, 96, 30, 30]
        elif total == 3:
            t_list = [107, 107, 30, 30]
        elif total == 2:
            t_list = [111, 96, 32, 32]
        elif total == 1:
            t_list = [110, 98, 37, 37]

        if is_raremon:
            t_list[1] = 96
            t_list[3] = 32
                    
    else:
        # 設定値なしの場合は戻る。
        return

    # 設定値の数値チェック/テキストボックスの設定
    for i in range(4):
        if t_list[i] < st.session_state[f"input_thresh{i}"]:
            st.session_state[f"input_thresh{i}"] = t_list[i]

    return



# モンスター名のセレクトボックス設定後、設定値に応じて相性閾値を変更する。
# min(m+s)の時これ。
def entry_set_th_from_cmb2(datalist):
    
    # 初期値設定
    total = 0
    is_raremon_c = False
    is_raremon_pg1 = False
    is_raremon_pg2 = False
    num_rare = 0  # レアモンスター用の変数（血統ID）
    entry_set_th2()

    # 閾値自動変更無効化チェック
    if st.session_state.input_threshs_chg_disabled:
        return

    # 設定値のカウント
    for i in range(len(st.session_state.select_options[0])):
        name = st.session_state[f'select_ops_name{i}']
        if name != "":
            total += 1
            df_monster = datalist.df_monsters[datalist.df_monsters["モンスター名"] == name]
            if not df_monster.empty and df_monster.iloc[0, 4] == num_rare:
                if i == 0:
                    is_raremon_c = True
                elif i <= 3:
                    is_raremon_pg1 = True
                else:
                    is_raremon_pg2 = True

    # 設定値に応じて、相性閾値を算出            
    if total != 0:
        st.session_state[f"input_thresh4"] = 70
        st.session_state[f"input_thresh5"] = 70
        st.session_state[f"input_thresh6"] = 70
        st.session_state[f"input_thresh7"] = 70

        if is_raremon_c:
            st.session_state[f"input_thresh4"] = 64
            st.session_state[f"input_thresh5"] = 64
            st.session_state[f"input_thresh6"] = 64
            st.session_state[f"input_thresh7"] = 64
        
        if is_raremon_pg1:
            st.session_state[f"input_thresh4"] = 64
            st.session_state[f"input_thresh6"] = 64
        
        if is_raremon_pg2:
            st.session_state[f"input_thresh5"] = 64
            st.session_state[f"input_thresh7"] = 64
        
        if total >= 5:
            st.session_state[f"input_thresh2"] = 1
            st.session_state[f"input_thresh3"] = 1
            st.session_state[f"input_thresh4"] = 1
            st.session_state[f"input_thresh5"] = 1
            st.session_state[f"input_thresh6"] = 1
            st.session_state[f"input_thresh7"] = 1

    else:
        pass

    return



# セレクトボックスで値設定後のモンスター名リストの整形
# ★streamlitでオプションリストの再構成を実施すると、
# ★リストの大本を参照しているのか、キーが""となってしまうため、再設定する。
def select_set_ops(datalist, who):

    # 設定値の保存
    name_mons = st.session_state[f"select_ops_name{who}"]
    name_main = st.session_state[f"select_ops_main{who}"]
    name_sub = st.session_state[f"select_ops_sub{who}"]

    # 設定変更されたセレクトボックスを判定して、参照元DataFrameを設定
    if who == 0:
        df = st.session_state.session_datalist.df_monsters_c
    else:
        df = st.session_state.session_datalist.df_monsters_pg

    # メイン血統を考慮して、モンスター名から不要レコードを削除
    if st.session_state[f"select_ops_main{who}"] != "":
        df = df[df["主血統"] == st.session_state[f"select_ops_main{who}"]]

    # サブ血統を考慮して、モンスター名から不要レコードを削除
    if st.session_state[f"select_ops_sub{who}"] != "":
        df = df[df["副血統"] == st.session_state[f"select_ops_sub{who}"]]
    
    # 主血統除いた場合のテーブルを使用したときの処理（純血統除外）
    if who == 0 and int(st.session_state.radio_c[0]) == DataList.choice_table_ex_org:
        df = df[df["主血統"] != df["副血統"]]
    if who !=0 and int(st.session_state.radio_pg[0]) == DataList.choice_table_ex_org:
        df = df[df["主血統"] != df["副血統"]]

    # それぞれリストに変換して、必要に応じて重複を削除し、先頭に空白を設定。
    # モンスター名
    df = df.sort_values(['主血統ID', 'モンスター名'], ascending=[True, True])
    lis1 = df.iloc[:, 0].to_list()
    lis1.insert(0, "")

    # メイン血統
    df_temp = df.drop_duplicates(subset="主血統")
    lis2 = df_temp.iloc[:, 1].to_list()
    lis2.insert(0, "")
    
    # サブ血統
    df = df.sort_values(['副血統ID', 'モンスター名'], ascending=[True, True])
    df_temp = df.drop_duplicates(subset="副血統")
    lis3 = df_temp.iloc[:, 2].to_list()
    lis3.insert(0, "")
    
    # 設定
    st.session_state.select_options[0][who]=lis1
    st.session_state.select_options[1][who]=lis2
    st.session_state.select_options[2][who]=lis3

    # 一時退避していた値を元に戻す
    st.session_state[f"select_ops_name{who}"] = ""
    st.session_state[f"select_ops_main{who}"] = name_main
    st.session_state[f"select_ops_sub{who}"]  = name_sub

    # 閾値再設定
    if name_mons != "":
        entry_set_th_from_cmb(datalist)
        pass

    return



# セレクトボックスの初期化
def reset_select_box(datalist, is_reset=True, is_child=True, is_parent=True):
    
    # モンスター名のコンボボックス参照リストの初期化
    if is_child:
        radio_set_c_cmb_th(datalist, is_reset)

    if is_parent:
        radio_set_pg_cmb_th(datalist, is_reset)
    
    # for文の範囲決定
    start = 0
    end   = 0
    if is_child and is_parent:
        # 全初期化
        start = 0
        end   = DataList.num_monster
    elif is_child:
        # 子のみ初期化
        start = 0
        end   = 1
    elif is_parent:
        # 親系列のみ初期化
        start = 1
        end   = DataList.num_monster

    # コンボボックスの内容とか初期化
    for i in range(start, end):
        st.session_state.session_datalist.lis_names[0][i] = ""
        st.session_state.session_datalist.lis_names[1][i] = ""
        st.session_state.session_datalist.lis_names[2][i] = ""
        st.session_state[f"select_ops_name{i}"] = ""
        st.session_state[f"select_ops_main{i}"] = ""
        st.session_state[f"select_ops_sub{i}"] = ""
        st.session_state.select_options[1][i] = datalist.lis_main_ped
        st.session_state.select_options[2][i] = datalist.lis_sub_ped
    
    # ラジオボタンの変更から起動した場合、閾値再設定(^はxorの意味)
    if is_child ^ is_parent:
        entry_set_th_from_cmb(datalist)

    return



# 検索開始ボタン押下後の動作
def button_calc_affinity(datalist):
    
    ### 事前設定

    # 検索フラグをON
    st.session_state.is_search_once_more = True

    # ログのクリア
    init_log()

    # 実行時刻を出力
    write_log("========================" + datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + "========================")


    ### 設定画面で設定した内容を各変数に再格納。

    # モンスター名の設定
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:  
        child = Monster(st.session_state.session_datalist.lis_names[0][0])
    elif int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
        child   = Monster(st.session_state.session_datalist.lis_names[0][0], st.session_state.session_datalist.lis_names[1][0], st.session_state.session_datalist.lis_names[2][0])
    parent1 = Monster(st.session_state.session_datalist.lis_names[0][1])
    granpa1 = Monster(st.session_state.session_datalist.lis_names[0][2])
    granma1 = Monster(st.session_state.session_datalist.lis_names[0][3])
    parent2 = Monster(st.session_state.session_datalist.lis_names[0][4])
    granpa2 = Monster(st.session_state.session_datalist.lis_names[0][5])
    granma2 = Monster(st.session_state.session_datalist.lis_names[0][6])
    Monster_info = [child, parent1, granpa1, granma1, parent2, granpa2, granma2]

    # 主血統/副血統の設定
    for i in range(len(Monster_info)):
        Monster_info[i].set_pedigree(datalist.df_monsters)

    # 相性値閾値設定
    thresh_aff = ThreshAff(st.session_state[f"input_thresh0"], st.session_state[f"input_thresh1"],
                           st.session_state[f"input_thresh2"], st.session_state[f"input_thresh3"], 
                           st.session_state[f"input_thresh4"], st.session_state[f"input_thresh5"], 
                           st.session_state[f"input_thresh6"], st.session_state[f"input_thresh7"])
    
    # テーブル取得
    set_using_table(datalist)

    # ログの設定
    set_log(Monster_info, thresh_aff)
    

    ### 相性値計算実行

    # 相性計算
    start_time = time.perf_counter()
    ret, df_affinities = calc_affinity(Monster_info, thresh_aff, datalist)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    write_log(f"◎処理時間： {elapsed_time:.1f}秒")

    # エラー処理(処理して条件が合えば、以下の処理、合わなければ、書き込み無効化までジャンプ)
    if ret :
        # テーブルの整形
        del df_affinities["index"]

    else:
        # 何もしないで次へ
        pass

    # 一時保存場所に設定
    st.session_state.session_datalist.df_affinities = df_affinities

    return ret



# 検索結果のチェックボックスをつけてからの再検索関数
def select_calc_affinity(datalist, selected_rows):
    
    # モンスター名の設定
    child = Monster()
    parent1 = Monster(selected_rows.iloc[-1,2])
    granpa1 = Monster(selected_rows.iloc[-1,3])
    granma1 = Monster(selected_rows.iloc[-1,4])
    parent2 = Monster(selected_rows.iloc[-1,5])
    granpa2 = Monster(selected_rows.iloc[-1,6])
    granma2 = Monster(selected_rows.iloc[-1,7])
    Monster_info = [child, parent1, granpa1, granma1, parent2, granpa2, granma2]

    # 主血統/副血統の設定
    for i in range(len(Monster_info)):
        Monster_info[i].set_pedigree(datalist.df_monsters)
    
    # テーブル取得
    set_using_table(datalist)
    
    # 相性計算
    df_affinities = calc_affinity_select(Monster_info, datalist)

    # テーブルの整形
    del df_affinities["index"]

    # 一時保存場所に設定
    st.session_state.session_datalist.df_affinities_slct = df_affinities

    return



# 相性値計算時に使用するテーブルを取得
def set_using_table(datalist):

    # 使用する変数の再格納
    df_monsters = datalist.df_monsters_del

    # オプション確認
    if st.session_state.session_datalist.lis_choice_table[0] == DataList.choice_table_org:
        lis_mons_league_tb_c = copy.deepcopy(datalist.lis_mons_league_tb_org)
    elif st.session_state.session_datalist.lis_choice_table[0] == DataList.choice_table_all:
        lis_mons_league_tb_c = copy.deepcopy(datalist.lis_mons_league_tb_all)
    elif st.session_state.session_datalist.lis_choice_table[0] == DataList.choice_table_ex_org:
        lis_mons_league_tb_c = copy.deepcopy(datalist.lis_mons_league_tb_ex_org)
        
    if st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_org:
        lis_mons_league_tb_pg = copy.deepcopy(datalist.lis_mons_league_tb_org)
    elif st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_all:
        lis_mons_league_tb_pg = copy.deepcopy(datalist.lis_mons_league_tb_all)
    elif st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_ex_org:
        lis_mons_league_tb_pg = copy.deepcopy(datalist.lis_mons_league_tb_ex_org)
    
    # モンスターの削除
    for mons_name in st.session_state.del_mons_list:
        
        df_temp = df_monsters[ mons_name == df_monsters["モンスター名"] ]
        main_id = df_temp.iloc[0, 3]
        sub_id = df_temp.iloc[0, 4]
        lis_mons_league_tb_c[main_id][sub_id] = "-"
        lis_mons_league_tb_pg[main_id][sub_id] = "-"
    
    # 設定
    st.session_state.session_datalist.lis_mons_league_tb_c  = lis_mons_league_tb_c
    st.session_state.session_datalist.lis_mons_league_tb_pg = lis_mons_league_tb_pg

    return


