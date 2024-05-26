"""
   Copyright 2024/5/18 sean of copyright owner

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
import streamlit as st

import pandas as pd

import datetime
import os
import time
from enum import Enum



# モンスターの情報を取り扱うクラス。
class Monster():
    
    def __init__(self):
        self.name = ""      #  モンスター名
        self.pedigree1 = "" #  主血統
        self.pedigree2 = "" #  副血統
        self.ped1_num  = 99 #  主血統ID（モンスター名をあいうえお順に並び変えて割り振ったID。レアモンは使わないが0に設定。）
        self.ped2_num  = 99 #  副血統ID（モンスター名をあいうえお順に並び変えて割り振ったID。レアモンは0に設定。）
    
    def __init__(self, name="", pedigree1="", pedigree2="", ped1_num=99, ped2_num=99):
        self.name = name 
        self.pedigree1 = pedigree1
        self.pedigree2 = pedigree2
        self.ped1_num  = ped1_num
        self.ped2_num  = ped2_num
    
    # テーブル情報を使用してモンスター名から主血統/副血統関連の情報をセットするメソッド。
    def set_pedigree(self, df_monsters):

        pedigree_num = df_monsters["主血統ID"].max()  # 主血統の個数（レアモン含まない。）
        df_monster = df_monsters[df_monsters["モンスター名"] == self.name]

        if not df_monster.empty:
            self.pedigree1 = df_monster.iloc[0, 1]
            self.pedigree2 = df_monster.iloc[0, 2]
            self.ped1_num  = [df_monster.iloc[0, 3]]
            self.ped2_num  = [df_monster.iloc[0, 4]]
        else:
            self.ped1_num = [i for i in range(pedigree_num+1)] # レアモン分を忘れずに加算。(0行目に置いている影響で必要。)
            self.ped2_num = [i for i in range(pedigree_num+1)] # レアモン分を忘れずに加算。
    
    def info(self):
        print(f"==================================")
        print(f"         Name: " + self.name)
        print(f"Main Pedegree: {self.ped1_num} {self.pedigree1}")



# 相性値計算時の閾値保管用クラス
class ThreshAff():
    
    def __init__(self):
        # 以下の値未満の相性値の場合、計算をスキップしている。
        self.th_ped1_cpg = 112  #  子-親-祖父-祖母間の主血統相性値閾値
        self.th_ped2_cpg = 96   #  子-親-祖父-祖母間の副血統相性値閾値
        self.th_ped1_pp = 35    #  親①-親②間の主血統相性値閾値
        self.th_ped2_pp = 32    #  親①-親②間の副血統相性値閾値
        self.th_p1 = 75         #  子-親①間の主/副血統相性値合計閾値
        self.th_p2 = 75         #  子-親②間の主/副血統相性値合計閾値
        self.th_cpg1 = 30       #  親①家系の子-祖 or 親-祖間の主/副血統相性値合計閾値
        self.th_cpg2 = 30       #  親②家系の子-祖 or 親-祖間の主/副血統相性値合計閾値

    
    def __init__(self, th_ped1_cpg=112, th_ped2_cpg=96, th_ped1_pp=35, th_ped2_pp=32, th_p1=75, th_p2=75, th_cpg1=70, th_cpg2=70):
        self.th_ped1_cpg = th_ped1_cpg
        self.th_ped2_cpg = th_ped2_cpg
        self.th_ped1_pp = th_ped1_pp
        self.th_ped2_pp = th_ped2_pp
        self.th_p1 = th_p1
        self.th_p2 = th_p2
        self.th_cpg1 = th_cpg1
        self.th_cpg2 = th_cpg2
        
    
    def info(self):
        print(f"子-親-祖父-祖母メイン血統の相性値閾値　　　　　　　　　　：{self.th_ped1_cpg}")
        print(f"子-親-祖父-祖母サブ血統の相性値閾値　　　　　　　　　　　：{self.th_ped2_cpg}")
        print(f"親①-親②メイン血統の相性値閾値　　　　　　　　　　　　　　：{self.th_ped1_pp}")
        print(f"親①-親②サブ血統の相性値閾値　　　　　　　　　　　　　　　：{self.th_ped2_pp}")
        print(f"子-親①間のメイン/サブ血統相性値合計閾値　　　　　　　　　：{self.th_p1}")
        print(f"子-親②間のメイン/サブ血統相性値合計閾値　　　　　　　　　：{self.th_p2}")
        print(f"親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{self.th_cpg1}")
        print(f"親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{self.th_cpg2}")



# データをまとめるクラス
class DataList():
    def __init__(self):

        # 設定値
        self.num_monster = 7
        self.num_kind = 3

        # 各入力データの格納場所
        self.df_monsters = pd.DataFrame()
        self.df_affinities_m_cp = pd.DataFrame()
        self.lis_affinities_m_cp = [[]]
        self.df_affinities_s_cp = pd.DataFrame()
        self.lis_affinities_s_cp = [[]]

        # 相性値事前計算①(min(m), min(m+s)用)結果格納場所
        self.lis_affinities_m_cpg = [[[[]]]]
        self.lis_affinities_s_cpg = [[[[]]]]

        # 相性値事前計算②(min(m+s)用)結果格納場所
        self.lis_affinities_m_s_cp = [[[[]]]]

        # モンスター参照用のリーグ表(3種)
        self.lis_mons_league_tb_all     = [[]]
        self.lis_mons_league_tb_all_org = [[]]
        self.lis_mons_league_tb_org     = [[]]
        self.lis_mons_league_tb_c       = [[]]
        self.lis_mons_league_tb_pg      = [[]]

        # ラジオボタン選択結果(テーブル情報)保存用格納域
        self.lis_choice_table = [0] * 2

        # コンボリスト用リスト/DF(create_combo_list参照)
        self.lis_main_ped = []
        self.lis_sub_ped = []
        self.lis_mons_names = []

        self.df_monsters_org = pd.DataFrame()
        self.lis_mons_names_org = []
        
        self.df_monsters_ex_org = pd.DataFrame()
        self.lis_mons_names_ex_org = []

        self.df_monsters_c = pd.DataFrame()
        self.df_monsters_pg = pd.DataFrame()

        # 検索用名前格納用リスト
        self.lis_names = [ [ "" for j in range(self.num_monster) ] for i in range(self.num_kind)]

        # 相性閾値の初期値設定用リスト(起動直後のみ、それ以降は使用しない。)
        self.lis_threshs = [0, 0, 34, 32, 75, 75, 75, 75]



# ラジオボタンの選択肢1
class RadioChoiceTable1(Enum):
  def __str__(cls):
    return cls.name

  min_m式 = 0
  min_m十s式 = 1



# ラジオボタンの選択肢2
class RadioChoiceTable2(Enum):
  def __str__(cls):
    return cls.name

  純血統十レア = 0
  全モンスター = 1
  全モンスター_純血統のみ除く = 2



## 入力ファイル名を変数に設定
## (入力ファイル名前/数は現状固定のため、ファイル名は受け取らず内部で直接宣言。)
def set_input_filename():
    
    # 変数初期化
    ret = False
    dic_file_names = {}

    # ファイル名の変数格納
    fname_monsters   = "data/monsters.csv"
    fname_affinities_main = "data/affinities_main.csv"
    fname_affinities_sub = "data/affinities_sub.csv"

    # 存在チェック
    if not os.path.isfile(os.getcwd() + "/" + fname_monsters):
        st.error(os.getcwd() + "/" + fname_monsters + "が存在しません。適切な場所にファイルを格納して再起動してください。")
        return ret, dic_file_names
    if not os.path.isfile(os.getcwd() + "/" + fname_affinities_main):
        st.error(os.getcwd() + "/" + fname_affinities_main + "が存在しません。適切な場所にファイルを格納して再起動してください")
        return ret, dic_file_names
    if not os.path.isfile(os.getcwd() + "/" + fname_affinities_sub):
        st.error(os.getcwd() + "/" + fname_affinities_sub + "が存在しません。適切な場所にファイルを格納して再起動してください")
        return ret, dic_file_names
    
    # 返却値格納
    ret = True
    dic_file_names = {"monsters":fname_monsters, 
                 "affinities_main":fname_affinities_main,
                 "affinities_sub":fname_affinities_sub}
    
    return ret, dic_file_names



## 各種データの読み込み+listへの変換
def read_all_data(dic_names):
    
    # 格納先の生成
    datalist = DataList()

    # csvの読み込み + list変換
    datalist.df_monsters = pd.read_csv(dic_names["monsters"])
    datalist.df_affinities_m_cp = pd.read_csv(dic_names["affinities_main"], index_col=0)
    datalist.lis_affinities_m_cp = datalist.df_affinities_m_cp.values.tolist()
    datalist.df_affinities_s_cp = pd.read_csv(dic_names["affinities_sub"], index_col=0)
    datalist.lis_affinities_s_cp = datalist.df_affinities_s_cp.values.tolist()

    # ★計算手法変更時確認★ 両方使用する予定あるから、事前計算はどちらのテーブルも実施しておく。

    # 事前計算①(min(m)用。)
    datalist.lis_affinities_m_cpg = precalc_affinity_cpg(datalist.lis_affinities_m_cp)
    datalist.lis_affinities_s_cpg = precalc_affinity_cpg(datalist.lis_affinities_s_cp)

    # 事前計算②(min(m+s)用。)
    datalist.lis_affinities_m_s_cp = precalc_affinity_m_s_cp(datalist.lis_affinities_m_cp, datalist.lis_affinities_s_cp)

    return datalist



## モンスター名リストに対して、相性表を参照して主血統ID/副血統IDの列を追加する。
## 返り値注意。(追加出来たらTrue,追加できなかったらFalse)
## また、モンスター名リストで不具合があればサイレントで削除する。
def add_monster_id(datalist):

    # 変数初期化
    ret = False

    # 使用する変数の再格納
    df_monsters = datalist.df_monsters

    # 主血統ID/副血統ID列を初期化
    df_monsters["主血統ID"] = -1
    df_monsters["副血統ID"] = -1
    
    # メイン血統相性表、サブ血統相性表の各インデックス名/列名を取得
    name_list_m_row = datalist.df_affinities_m_cp.index.to_list()
    name_list_m_col = datalist.df_affinities_m_cp.columns.to_list()
    name_list_s_row = datalist.df_affinities_s_cp.index.to_list()
    name_list_s_col = datalist.df_affinities_s_cp.columns.to_list()

    ## 相性表の対応関係に問題ないかをチェック
    # チェック用のローカル関数を作成
    def is_same_list(list1, list2):
        # 長さチェック
        if len(list1) != len(list2):
            return False
        # モンスター名チェック
        for i in range(len(list1)):
            if list1[i] != list2[i]:
                return False
        return True
    
    # メイン血統のインデックス名/列名で順番が同じになっているかチェック
    if not is_same_list(name_list_m_row, name_list_m_col):
        st.error("affinities_main.csvのインデックス名/列名の対応関係がとれていません。\n同じ順番にしてください。")
        return ret

    # サブ血統のインデックス名/列名で順番が同じになっているかチェック
    if not is_same_list(name_list_s_row, name_list_s_col):
        st.error("affinities_sub.csvのインデックス名/列名の対応関係がとれていません。\n同じ順番にしてください。")
        return ret

    # メイン血統のインデックス名/サブ血統のインデックス名で順番が同じになっているかチェック
    if not is_same_list(name_list_m_row, name_list_s_row):
        st.error("affinities_main.csvとaffinities_main.csvで対応関係がとれていません。\n同じ形式の表にしてください。")
        return ret

    # 0番目の行/列がレアになっているかチェック（以降、0番目をレアモンとして処理しているため、事前にチェック）
    if name_list_m_row[0] != "レア":
        st.error("affinities_main.csv, affinities_main.csvともに1行目/1列目が\nレアモンの情報ではありません。\n必ず1行目/1列目はレアモンの情報を設定してください。")
        return ret

    # 代表してメイン血統のインデックス名を使用して、df_monstersにIDを追加する
    for i, name in enumerate(name_list_m_row):
        df_monsters.loc[df_monsters["主血統"] == name, "主血統ID" ] = i
        df_monsters.loc[df_monsters["副血統"] == name, "副血統ID" ] = i

    # df_monsters中の"主血統ID"または"副血統ID"が-1のレコードは問答無用で削除する。(バグの元となるため。）
    len_before = len(df_monsters)
    df_monsters = df_monsters.drop(df_monsters[df_monsters['主血統ID'] == -1].index)
    df_monsters = df_monsters.drop(df_monsters[df_monsters['副血統ID'] == -1].index)
    len_after = len(df_monsters)

    # チェックで削除があった場合は念のため通知しておく。
    if len_before != len_after:
        st.warning(f"主血統名/副血統名に問題があったため、全{len_before}件から{len_before - len_after}件削除しました。必要に応じてmonsters.csvを見直してください。")

    # 正常動作
    ret = True

    # 変数をdatalistに格納
    datalist.df_monsters = df_monsters

    return ret



## モンスター名リストに対して、検索タグ用のレアモンを追加し、ソートする。
def add_raremon(datalist):
    
    # 使用する変数の再格納
    df_monsters = datalist.df_monsters

    # 名前比較用のリストを準備
    name_list_m_row = datalist.df_affinities_m_cp.index.to_list()
    name_list_m_row.remove("レア")

    # レアモンタグのついたレコードの主血統名を抽出
    df_temp = df_monsters[df_monsters["モンスター名"].str.startswith('(●レア)')]
    name_list_raremon_m = df_temp.iloc[:, 1].to_list()

    # レアモンタグのついたレコードの主血統名のリスト内に、比較用リストの名前がない場合にレコードを追加
    for i, name in enumerate(name_list_m_row):
        if name not in name_list_raremon_m:
            df_monsters.loc[f'temp{i}'] = [f'(●レア){name}', name, 'レア', i+1, 0]
    
    # モンスター名のファイルのみソート
    df_monsters = df_monsters.sort_values(['主血統ID', 'モンスター名'], ascending=[True, True])

    # インデックスをリセットして、新たに発生するindex列を削除
    df_monsters = df_monsters.reset_index()
    del df_monsters['index']

    # 変数をdatalistに格納
    datalist.df_monsters = df_monsters

    # debug
    # df_temp = df_monsters[["モンスター名", "主血統", "副血統"]]
    # df_temp.to_csv("temp_mons.csv", index=False)
    # debug

    return



# モンスター名リストからリーグ表を3種作成
# ★所持モンスターチェックをつける場合について
# 　　原本はそのままにしておいて、どこかで最初に変更して、その変更後のDFを以降の処理参照するようにする。
def create_league_table(datalist):
    
    # モンスター名リストをlistに変換
    lis_monsters = datalist.df_monsters.values.tolist()

    # リーグ表用のリストの初期化
    length = len(datalist.lis_affinities_m_cp)
    lis_mons_league_tb_all     = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_all_org = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_org     = [[ "-" for i in range(length)] for i in range(length)]
    
    # レアモンスター用の変数（血統ID、名前保存場所）
    num_rare = 0
    name_rare = "(●レア)"  # "(●レア)"とついたモンスター名を保存する場所。

    # モンスター名リスト → リーグ表に変換
    for row in lis_monsters:
        if lis_mons_league_tb_all[row[3]][row[4]] == "-":
            if row[0].startswith(name_rare):
                # タグ用のレアモンスター名があってもリーグ表には追加しない。
                continue
            if row[4] == num_rare:
                lis_mons_league_tb_all[row[3]][row[4]]     = name_rare + row[1]
                lis_mons_league_tb_all_org[row[3]][row[4]] = name_rare + row[1]
                lis_mons_league_tb_org[row[3]][row[4]]     = name_rare + row[1]
            else:
                lis_mons_league_tb_all[row[3]][row[4]]     = row[0]
                lis_mons_league_tb_all_org[row[3]][row[4]] = row[0]
                
        if row[3] == row[4]:
            lis_mons_league_tb_all_org[row[3]][row[4]]     = "-"
            lis_mons_league_tb_org[row[3]][row[4]]         = row[0]
    
    # 設定
    datalist.lis_mons_league_tb_all     = lis_mons_league_tb_all
    datalist.lis_mons_league_tb_all_org = lis_mons_league_tb_all_org
    datalist.lis_mons_league_tb_org     = lis_mons_league_tb_org

    # debug start
    # temp1 = pd.DataFrame(datalist.lis_mons_league_tb_all_org)
    # temp2 = pd.DataFrame(datalist.lis_mons_league_tb_org)
    # temp3 = pd.DataFrame(datalist.lis_mons_league_tb_all)
    # temp1.to_csv("temp1.csv")
    # temp2.to_csv("temp2.csv")
    # temp3.to_csv("temp3.csv")
    # debug end

    return



## セレクトボックスの初期リスト作成
def create_combo_list(datalist):

    # 使用する変数の再格納
    df_monsters = datalist.df_monsters

    # メイン血統の絞込み用リスト
    datalist.lis_main_ped = datalist.df_affinities_m_cp.index.to_list()
    datalist.lis_main_ped[0] = ""  # レアモン削除処理 兼 リセット用空白セット処理
    
    # サブ血統の絞込み用リスト
    datalist.lis_sub_ped = datalist.df_affinities_s_cp.index.to_list()
    datalist.lis_sub_ped.insert(0, "")

    # 全モンスター名のリスト
    datalist.lis_mons_names = datalist.df_monsters.iloc[:, 0].to_list()
    datalist.lis_mons_names.insert(0, "")

    # 主血統+レアの名前リスト
    datalist.df_monsters_org = df_monsters[(df_monsters["主血統"] == df_monsters["副血統"]) | (df_monsters["モンスター名"].str.startswith('(●レア)'))].copy()
    datalist.lis_mons_names_org = datalist.df_monsters_org.iloc[:, 0].to_list()
    datalist.lis_mons_names_org.insert(0, "")

    # 主血統のみ除く全モンスター名リスト
    datalist.df_monsters_ex_org = df_monsters[df_monsters["主血統"] != df_monsters["副血統"]].copy()
    datalist.lis_mons_names_ex_org = datalist.df_monsters_ex_org.iloc[:, 0].to_list()
    datalist.lis_mons_names_ex_org.insert(0, "")

    # セレクトボックスの絞込み用のDataFrame型を用意。
    datalist.df_monsters_c = df_monsters
    datalist.df_monsters_pg = df_monsters

    # 変数をdatalistに格納
    datalist.df_monsters = df_monsters

    return



## ラジオボタン変更後の処理（子のコンボリスト関連の設定）
def radio_set_c_cmb_th(datalist, is_reset=False):

    # 前回値から変更があったかの確認
    if st.session_state.radio_c.value != st.session_state.radio_c_prev.value or is_reset:

        # 前回値に今回設定値を保存
        st.session_state.radio_c_prev = st.session_state.radio_c

        # テーブルの設定
        if st.session_state.radio_c.value == 0:
            st.session_state.select_options[0][0] = datalist.lis_mons_names_org
            datalist.df_monsters_c = datalist.df_monsters_org
        elif st.session_state.radio_c.value == 1:
            st.session_state.select_options[0][0] = datalist.lis_mons_names
            datalist.df_monsters_c = datalist.df_monsters
        else:
            st.session_state.select_options[0][0] = datalist.lis_mons_names_ex_org
            datalist.df_monsters_c = datalist.df_monsters_ex_org
        
        # 閾値の再設定
        entry_set_th(st.session_state.radio_calc.value)

    return



## ラジオボタン変更後の処理（親祖父母のコンボリスト関連の設定）
def radio_set_pg_cmb_th(datalist, is_reset=False):

    # 前回値から変更があったかの確認
    if st.session_state.radio_pg.value != st.session_state.radio_pg_prev.value or is_reset:

        # 前回値に今回設定値を保存
        st.session_state.radio_pg_prev = st.session_state.radio_pg

        # テーブルの設定
        if st.session_state.radio_pg.value == 0:
            for i in range(datalist.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names_org
            datalist.df_monsters_pg = datalist.df_monsters_org
        elif st.session_state.radio_pg.value == 1:
            for i in range(datalist.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names
            datalist.df_monsters_pg = datalist.df_monsters
        else:
            for i in range(datalist.num_monster-1):
                st.session_state.select_options[0][i+1] = datalist.lis_mons_names_ex_org
            datalist.df_monsters_pg = datalist.df_monsters_ex_org
        
        # 閾値の再設定
        entry_set_th(st.session_state.radio_calc.value)

    return



# テキストボックスの内容更新
# ★同じような処理で、別の設定にするなら、親関数作って、そこでフラグを分けて、子関数で処理するようにした方が管理しやすそう。以降も同じ。
def entry_set_th(flag):
    if flag == 0:
        entry_set_th1()
    elif flag == 1:
        entry_set_th2()
    return


# min(m)の場合のテキストボックス内閾値初期化
def entry_set_th1():

    # 入力域の無効化
    for i in range(8):
        if i < 4:
            st.session_state.input_threshs_disabled[i] = False
        else:
            st.session_state.input_threshs_disabled[i] = True

    # ラジオボタンの設定値取得、一部先行設定
    c_num = st.session_state.radio_c.value
    pg_num = st.session_state.radio_pg.value

    # ラジオボタンの内容に合わせてテキストボックスの内容を設定
    # 論理設計するともう少し最適化できそうだけど、いったんこれで。
    if c_num == 0 and pg_num == 0:
        st.session_state[f"input_thresh0"] = 109
        st.session_state[f"input_thresh1"] = 95
        st.session_state[f"input_thresh2"] = 33
        
    elif c_num == 0 and pg_num == 1:
        st.session_state[f"input_thresh0"] = 117
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 36
        
    elif c_num == 0 and pg_num == 2:
        st.session_state[f"input_thresh0"] = 115
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 36
        
    elif c_num == 1 and pg_num == 0:
        st.session_state[f"input_thresh0"] = 110
        st.session_state[f"input_thresh1"] = 95
        st.session_state[f"input_thresh2"] = 35
    
    elif c_num == 1 and pg_num == 1:
        st.session_state[f"input_thresh0"] = 117
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 38
        
    elif c_num == 1 and pg_num == 2:
        st.session_state[f"input_thresh0"] = 116
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 38
        
    elif c_num == 2 and pg_num == 0:
        st.session_state[f"input_thresh0"] = 109
        st.session_state[f"input_thresh1"] = 95
        st.session_state[f"input_thresh2"] = 33
        
    elif c_num == 2 and pg_num == 1:
        st.session_state[f"input_thresh0"] = 117
        st.session_state[f"input_thresh1"] = 96
        st.session_state[f"input_thresh2"] = 38
    
    elif c_num == 2 and pg_num == 2:
        st.session_state[f"input_thresh0"] = 116
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
    for i in range(8):
        if i < 2:
            st.session_state.input_threshs_disabled[i] = True
        else:
            st.session_state.input_threshs_disabled[i] = False

    # 初期値設定
    st.session_state[f"input_thresh0"] = 0
    st.session_state[f"input_thresh1"] = 0
    st.session_state[f"input_thresh2"] = 34
    st.session_state[f"input_thresh3"] = 32
    st.session_state[f"input_thresh4"] = 75
    st.session_state[f"input_thresh5"] = 75
    st.session_state[f"input_thresh6"] = 75
    st.session_state[f"input_thresh7"] = 75

    return



# モンスター名のセレクトボックス設定後、設定値に応じて相性閾値を変更する。
def entry_set_th_from_cmb(flag, datalist):
    if flag == 0:
        entry_set_th_from_cmb1()
    elif flag == 1:
        entry_set_th_from_cmb2(datalist)
    return


# モンスター名のセレクトボックス設定後、設定値に応じて相性閾値を変更する。
# min(m)の時これ。
def entry_set_th_from_cmb1():
    
    # 初期値設定
    total = 0
    cnt_list = [0] * len(st.session_state.select_options[0])
    t_list = []

    # 設定値のカウント
    for i in range(len(st.session_state.select_options[0])):
        if st.session_state[f'select_ops_name{i}'] != "":
            cnt_list[i] += 1
            total += 1

    # 設定値に応じて、相性閾値を算出
    if total >= 4:
        t_list = [96, 96, 30, 30]
    elif total == 3:
        t_list = [107, 107, 30, 30]
    elif total == 2:
        t_list = [111, 96, 32, 32]
    elif total == 1:
        if cnt_list[0] == 1 or cnt_list[4] == 1:
            t_list = [112, 96, 34, 32]
        else:
            t_list = [115, 96, 35, 32]
    else:
        # 設定値なしの場合は初期値を再設定し、戻る。
        entry_set_th1()
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

    else:
        entry_set_th2()

    return



# セレクトボックスで値設定後のモンスター名リストの整形
# ★streamlitでオプションリストの再構成を実施すると、
# ★リストの大本を参照しているのか、キーが""となってしまうため、再設定する。
def select_set_ops(datalist, who):

    # 設定値の保存
    name_main = st.session_state[f"select_ops_main{who}"]
    name_sub = st.session_state[f"select_ops_sub{who}"]

    # 設定変更されたセレクトボックスを判定して、参照元DataFrameを設定
    if who == 0:
        df = datalist.df_monsters_c
    else:
        df = datalist.df_monsters_pg

    # メイン血統を考慮して、モンスター名から不要レコードを削除
    if st.session_state[f"select_ops_main{who}"] != "":
        df = df[df["主血統"] == st.session_state[f"select_ops_main{who}"]]

    # サブ血統を考慮して、モンスター名から不要レコードを削除
    if st.session_state[f"select_ops_sub{who}"] != "":
        df = df[df["副血統"] == st.session_state[f"select_ops_sub{who}"]]

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
    child   = Monster(datalist.lis_names[0][0])
    parent1 = Monster(datalist.lis_names[0][1])
    granpa1 = Monster(datalist.lis_names[0][2])
    granma1 = Monster(datalist.lis_names[0][3])
    parent2 = Monster(datalist.lis_names[0][4])
    granpa2 = Monster(datalist.lis_names[0][5])
    granma2 = Monster(datalist.lis_names[0][6])
    Monster_info = [child, parent1, granpa1, granma1, parent2, granpa2, granma2]

    # 主血統/副血統の設定
    for i in range(len(Monster_info)):
        Monster_info[i].set_pedigree(datalist.df_monsters)

    # 相性値閾値設定
    # ★計算手法変更時確認★
    thresh_aff = ThreshAff(st.session_state[f"input_thresh0"], st.session_state[f"input_thresh1"],
                           st.session_state[f"input_thresh2"], st.session_state[f"input_thresh3"], 
                           st.session_state[f"input_thresh4"], st.session_state[f"input_thresh5"], 
                           st.session_state[f"input_thresh6"], st.session_state[f"input_thresh7"])
    
    # テーブル取得
    set_using_table(datalist)

    # ログの設定
    set_log(Monster_info, datalist.lis_choice_table, thresh_aff)
    

    ### 相性値計算実行/表示処理

    # 前回表示結果を削除
    # self.delete_tree()
    
    # 相性計算
    start_time = time.perf_counter()
    # ★計算手法変更時確認★
    # ret, self.df_affinities = self.calc_affinity(Monster_info, thresh_aff, lis_mons_league_tb_c, lis_mons_league_tb_pg)
    ret, st.session_state.df_affinities = calc_affinity_m_s(Monster_info, thresh_aff, datalist)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    write_log(f"◎処理時間： {elapsed_time:.1f}秒")

    # エラー処理(処理して条件が合えば、以下の処理、合わなければ、書き込み無効化までジャンプ)
    if ret :
        
        # テーブルの整形
        del st.session_state.df_affinities["index"]

    else:
        # 何もしないで次へ
        pass


    ### 後処理


    return ret



# 相性値計算時に使用するテーブルを取得
def set_using_table(datalist):

    # オプション確認
    if datalist.lis_choice_table[0].value == 0:
        lis_mons_league_tb_c = datalist.lis_mons_league_tb_org
    elif datalist.lis_choice_table[0].value == 1:
        lis_mons_league_tb_c = datalist.lis_mons_league_tb_all
    else:
        lis_mons_league_tb_c = datalist.lis_mons_league_tb_all_org
        
    if datalist.lis_choice_table[1].value == 0:
        lis_mons_league_tb_pg = datalist.lis_mons_league_tb_org
    elif datalist.lis_choice_table[1].value == 1:
        lis_mons_league_tb_pg = datalist.lis_mons_league_tb_all
    else:
        lis_mons_league_tb_pg = datalist.lis_mons_league_tb_all_org
    
    # 設定
    datalist.lis_mons_league_tb_c  = lis_mons_league_tb_c
    datalist.lis_mons_league_tb_pg = lis_mons_league_tb_pg

    return



# 相性基準のマークを返却。★ただし、相性閾値のこと全然知らないので、すべて仮値。
def get_mark(affinity):
    
    mark = "×"
    
    if affinity > 610:
        mark = "☆"
    elif affinity > 490:
        mark = "◎"
    elif affinity > 374:
        mark = "〇"
    elif affinity > 257:
        mark = "△"
    else:
        mark = "×"
    
    return mark



## 子/親/祖父母間相性値の事前計算関数。min(m)用
def precalc_affinity_cpg(lis_affinities_cp):

    # 子×親 + min(子×祖父, 親×祖父) + min(子×祖母, 親×祖母)の値を格納した4次元テーブル作成。
    # dim1：祖母、dim2：祖父、dim3：親、dim4:子
    
    # 3次元、4次元リスト作成
    length = len(lis_affinities_cp)
    work = [[[0 for i in range(length)] for j in range(length)] for k in range(length)]
    lis_affinities_cpg = [[[[0 for i in range(length)] for j in range(length)] for k in range(length)] for l in range(length)]
    
    # 計算…min(子×祖父, 親×祖父)参照用テーブル
    for child in range(length):
        for parent in range(length):
            for grand in range(length):
                cg = lis_affinities_cp[child][grand]
                pg = lis_affinities_cp[parent][grand]
                work[child][parent][grand] = cg if cg < pg else pg
    
    # 実テーブル
    for child in range(length):
        for parent in range(length):
            cp = lis_affinities_cp[child][parent]
            for granpa in range(length):
                for granma in range(length):
                    lis_affinities_cpg[child][parent][granpa][granma] = work[child][parent][granpa] + work[child][parent][granma] + cp
                    
    return lis_affinities_cpg



## 子→親系のメイン血統サブ血統合計値事前計算。min(m+s)用
def precalc_affinity_m_s_cp(lis_affinities_m_cp, lis_affinities_s_cp):

    # 子→親へのメイン血統相性値+サブ血統相性値の合計値を格納した4次元テーブル作成。
    # dim1：親サブ、dim2:親メイン、dim3:子サブ、dim4:子メイン

    # 4次元作成
    length = len(lis_affinities_m_cp)
    lis_affinities_m_s_cp = [[[[0 for i in range(length)] for j in range(length)] for k in range(length)] for l in range(length)]
    
    # 計算…min(子×祖父, 親×祖父)参照用テーブル
    for child1 in range(length):
        for child2 in range(length):
            for parent1 in range(length):
                for parent2 in range(length):
                    lis_affinities_m_s_cp[child1][child2][parent1][parent2]  = lis_affinities_m_cp[child1][parent1]  + lis_affinities_s_cp[child2][parent2]
                    
    return lis_affinities_m_s_cp



# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m)用
def calc_affinity(Monster_info, thresh_aff, lis_mons_league_tb_c, lis_mons_league_tb_pg):

    # 親①、親②毎に、（子の主血統/副血統、親の主血統/副血統番号）をキーとした
    # 相性値、モンスター名(子/親/祖父/祖母)の6次元配列作成。
    # 6, 5, 4, 3次元目は子の主血統/副血統、2次元目は各「相性値、モンスター名(子/親/祖父/祖母)」のリスト、1次元目で要素アクセス。
    # 2つ出し終わったら、子の主血統/副血統番号が一致するところで、
    # 親①、親②の相性チェックを実施(悪ければ次の親へ)して、親①×親②の相性値も足し合わせ、最終結果を算出。
    # （なお、子の名前の一致不一致で決めてもよいが、レアモンの処理をきちんとしていないため、今回は番号で確認とする。）
    # 最終結果の形式は、判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに格納し、
    # その後、データフレーム型に変換して、相性値で降順ソートして返却する。
    
    # 返却値
    ret = False
    N = 80000
    # 保管用リストの作成
    ped1_num = len(lis_mons_league_tb_c)
    ped2_num = len(lis_mons_league_tb_c)
    # lis_affinities_cpg1[child1][child2][parent1][parent2]
    lis_affinities_cpg1 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities_cpg2 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities      = []
    lis_child1          = []
    lis_child2          = [ [] for j in range(ped1_num) ]
    lis_parent1_1       = []
    lis_parent1_2       = [ [] for j in range(ped1_num) ]
    lis_parent2_1       = []
    lis_parent2_2       = [ [] for j in range(ped1_num) ]
    df_affinities       = pd.DataFrame( [] )
    
    # 子-親①-祖父①-祖母①のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    i = 0
    for child1 in Monster_info[0].ped1_num:
        for parent1 in Monster_info[1].ped1_num:
            for granpa1 in Monster_info[2].ped1_num:
                for granma1 in Monster_info[3].ped1_num:
                    # ここまでで主血統ループ
                    cpg1 = self.lis_affinities_m_cpg[child1][parent1][granpa1][granma1]
                    if cpg1 < thresh_aff.th_ped1_cpg:
                        continue
                    for child2 in Monster_info[0].ped2_num:
                        name_c = lis_mons_league_tb_c[child1][child2]
                        if name_c == "-":
                            continue
                        for parent2 in Monster_info[1].ped2_num:
                            name_p = lis_mons_league_tb_pg[parent1][parent2]
                            if name_p == "-":
                                continue
                            for granpa2 in Monster_info[2].ped2_num:
                                name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                                if name_g1 == "-":
                                    continue
                                for granma2 in Monster_info[3].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    # ここまでで副血統ループ
                                    cpg2 = self.lis_affinities_s_cpg[child2][parent2][granpa2][granma2]
                                    if cpg2 < thresh_aff.th_ped2_cpg:
                                        continue
                                    lis_affinities_cpg1[child1][child2][parent1][parent2].append([cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    # lis_affinities_cpg1.append([child1, child2, parent1, parent2, cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if child1 not in lis_child1:
                                        lis_child1.append(child1)
                                    if child2 not in lis_child2[child1]:
                                        lis_child2[child1].append(child2)
                                    if parent1 not in lis_parent1_1:
                                        lis_parent1_1.append(parent1)
                                    if parent2 not in lis_parent1_2[parent1]:
                                        lis_parent1_2[parent1].append(parent2)
                                    i += 1
    write_log(f"◎子-親①-祖父①-祖母②の組み合わせ：{i:,}件")
    if i >= N:
        st.error(f"候補が{N}件を超えたため停止します。\n閾値やリーグ表の見直しを実施してください。")
        return ret, df_affinities
    
    # 子-親②-祖父②-祖母②のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    j = 0
    for child1 in lis_child1:
        for parent1 in Monster_info[4].ped1_num:
            for granpa1 in Monster_info[5].ped1_num:
                for granma1 in Monster_info[6].ped1_num:
                    # ここまでで主血統ループ
                    cpg1 = self.lis_affinities_m_cpg[child1][parent1][granpa1][granma1]
                    if cpg1 < thresh_aff.th_ped1_cpg:
                        continue
                    for child2 in lis_child2[child1]:
                        name_c = lis_mons_league_tb_c[child1][child2]
                        # 子を指定して原種検索する場合にコメントアウト必要。
                        if name_c == "-":
                            continue
                        for parent2 in Monster_info[4].ped2_num:
                            name_p = lis_mons_league_tb_pg[parent1][parent2]
                            if name_p == "-":
                                continue
                            for granpa2 in Monster_info[5].ped2_num:
                                name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                                if name_g1 == "-":
                                    continue
                                for granma2 in Monster_info[6].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    # ここまでで副血統ループ
                                    cpg2 = self.lis_affinities_s_cpg[child2][parent2][granpa2][granma2]
                                    if cpg2 < thresh_aff.th_ped2_cpg:
                                        continue
                                    # name_cの格納は不要だが、同形状のリストの方がバグを回避できそうなためそのままとする。
                                    # lis_affinities_cpg2.append([child1, child2, parent1, parent2, cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    lis_affinities_cpg2[child1][child2][parent1][parent2].append([cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if parent1 not in lis_parent2_1:
                                        lis_parent2_1.append(parent1)
                                    if parent2 not in lis_parent2_2[parent1]:
                                        lis_parent2_2[parent1].append(parent2)
                                    j += 1
    write_log(f"◎子-親②-祖父②-祖母②の組み合わせ：{j:,}件")
    if j >= N:
        st.error(f"候補が{N}件を超えたため停止します。\n閾値やリーグ表の見直しを実施してください。")
        return ret, df_affinities
    
    # 親①-親②のメイン/サブ血統(基準値以下はスキップ)
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            for parent1_1 in lis_parent1_1:
                for parent2_1 in lis_parent2_1:
                    pp1 = self.lis_affinities_m_cp[ parent1_1 ][ parent2_1 ]
                    if pp1 < thresh_aff.th_ped1_pp:
                        continue
                    for parent1_2 in lis_parent1_2[parent1_1]:
                        for parent2_2 in lis_parent2_2[parent2_1]:
                            pp2 = self.lis_affinities_s_cp[ parent1_2 ][ parent2_2 ]
                            if pp2 < thresh_aff.th_ped2_pp:
                                continue
                            for cpg1_record in lis_affinities_cpg1[child1][child2][parent1_1][parent1_2]:
                                for cpg2_record in lis_affinities_cpg2[child1][child2][parent2_1][parent2_2]:
                                    affinity = pp1 + pp2 + cpg1_record[0] + cpg2_record[0]
                                    mark = self.get_mark(affinity)
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）
                                    lis_affinities.append([mark, affinity, 
                                                        cpg1_record[1], cpg1_record[2], 
                                                        cpg1_record[3], cpg1_record[4], 
                                                                        cpg2_record[2], 
                                                        cpg2_record[3], cpg2_record[4]] )

    # データフレーム型に変換してソート。
    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        write_log("候補0件。（他のログは出力しません。）")
        return ret, df_affinities

    df_affinities = pd.DataFrame( lis_affinities )
    df_affinities = df_affinities.sort_values([1, 2], ascending=[False, True])
    # df_affinities = df_affinities.sort_values([1, 2, 3, 4, 5, 6, 7, 8], ascending=[False, True, True, True, True, True, True, True])
    df_affinities.columns=['評価', '相性値', '子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']
    
    ret = True

    return ret, df_affinities.reset_index()



# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m+s)用。
def calc_affinity_m_s(Monster_info, thresh_aff, datalist):

    # 愚直に計算。
    # min(m)とやり方は近く、事前計算できなくなった分、本関数で追加で実施している箇所あり。
    
    # 返却値
    ret = False
    N = 80000
    # 参照高速化のためにローカル設定
    lis_affinities_m_s_cp   = datalist.lis_affinities_m_s_cp
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_s_cp     = datalist.lis_affinities_s_cp
    lis_mons_league_tb_c    = datalist.lis_mons_league_tb_c
    lis_mons_league_tb_pg   = datalist.lis_mons_league_tb_pg
    # 保管用リストの作成
    ped1_num = len(lis_mons_league_tb_c)
    ped2_num = len(lis_mons_league_tb_c)
    # lis_affinities_cpg1[child1][child2][parent1][parent2]
    lis_affinities_cpg1 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities_cpg2 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities      = []
    lis_child1          = []
    lis_child2          = [ [] for j in range(ped1_num) ]
    lis_parent1_1       = []
    lis_parent1_2       = [ [] for j in range(ped1_num) ]
    lis_parent2_1       = []
    lis_parent2_2       = [ [] for j in range(ped1_num) ]
    df_affinities       = pd.DataFrame( [] )

    # 子-親①-祖父①-祖母①のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    i = 0
    # 子
    for child1 in Monster_info[0].ped1_num:
        for child2 in Monster_info[0].ped2_num:
            name_c = lis_mons_league_tb_c[child1][child2]
            if name_c == "-":
                continue
            
            # 親
            for parent1 in Monster_info[1].ped1_num:
                for parent2 in Monster_info[1].ped2_num:
                    name_p = lis_mons_league_tb_pg[parent1][parent2]
                    if name_p == "-":
                        continue
                    cp = lis_affinities_m_s_cp[child1][child2][parent1][parent2]
                    if cp < thresh_aff.th_p1:
                        continue
                    
                    # 祖父
                    for granpa1 in Monster_info[2].ped1_num:
                        for granpa2 in Monster_info[2].ped2_num:
                            name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                            if name_g1 == "-":
                                continue
                            cg1 = lis_affinities_m_s_cp[child1][child2][granpa1][granpa2]
                            pg1 = lis_affinities_m_s_cp[parent1][parent2][granpa1][granpa2]
                            cpg1 = cg1 if cg1 < pg1 else pg1
                            if cpg1 < thresh_aff.th_cpg1:
                                continue

                            # 祖母
                            for granma1 in Monster_info[3].ped1_num:
                                for granma2 in Monster_info[3].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    cg2 = lis_affinities_m_s_cp[child1][child2][granma1][granma2]
                                    pg2 = lis_affinities_m_s_cp[parent1][parent2][granma1][granma2]
                                    cpg2 = cg2 if cg2 < pg2 else pg2
                                    if cpg2 < thresh_aff.th_cpg1:
                                        continue

                                    # 格納
                                    lis_affinities_cpg1[child1][child2][parent1][parent2].append([cp + cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if child1 not in lis_child1:
                                        lis_child1.append(child1)
                                    if child2 not in lis_child2[child1]:
                                        lis_child2[child1].append(child2)
                                    if parent1 not in lis_parent1_1:
                                        lis_parent1_1.append(parent1)
                                    if parent2 not in lis_parent1_2[parent1]:
                                        lis_parent1_2[parent1].append(parent2)
                                    i += 1
    write_log(f"◎子-親①-祖父①-祖母②の組み合わせ：{i:,}件")
    if i >= N:
        st.error(f"候補が{N}件を超えたため停止します。\n閾値やリーグ表の見直しを実施してください。")
        return ret, df_affinities
    
    # 子-親②-祖父②-祖母②のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    j = 0
    # 子
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            name_c = lis_mons_league_tb_c[child1][child2]
            if name_c == "-":
                continue
            
            # 親
            for parent1 in Monster_info[4].ped1_num:
                for parent2 in Monster_info[4].ped2_num:
                    name_p = lis_mons_league_tb_pg[parent1][parent2]
                    if name_p == "-":
                        continue
                    cp = lis_affinities_m_s_cp[child1][child2][parent1][parent2]
                    if cp < thresh_aff.th_p2:
                        continue

                    # 祖父
                    for granpa1 in Monster_info[5].ped1_num:
                        for granpa2 in Monster_info[5].ped2_num:
                            name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                            if name_g1 == "-":
                                continue
                            cg1 = lis_affinities_m_s_cp[child1][child2][granpa1][granpa2]
                            pg1 = lis_affinities_m_s_cp[parent1][parent2][granpa1][granpa2]
                            cpg1 = cg1 if cg1 < pg1 else pg1
                            if cpg1 < thresh_aff.th_cpg2:
                                continue

                            # 祖母
                            for granma1 in Monster_info[6].ped1_num:
                                for granma2 in Monster_info[6].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    cg2 = lis_affinities_m_s_cp[child1][child2][granma1][granma2]
                                    pg2 = lis_affinities_m_s_cp[parent1][parent2][granma1][granma2]
                                    cpg2 = cg2 if cg2 < pg2 else pg2
                                    if cpg2 < thresh_aff.th_cpg2:
                                        continue

                                    # 格納
                                    # name_cの格納は不要だが、同形状のリストの方がバグを回避できそうなためそのままとする。
                                    lis_affinities_cpg2[child1][child2][parent1][parent2].append([cp + cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if parent1 not in lis_parent2_1:
                                        lis_parent2_1.append(parent1)
                                    if parent2 not in lis_parent2_2[parent1]:
                                        lis_parent2_2[parent1].append(parent2)
                                    j += 1
    write_log(f"◎子-親②-祖父②-祖母②の組み合わせ：{j:,}件")
    if j >= N:
        st.error(f"候補が{N}件を超えたため停止します。\n閾値やリーグ表の見直しを実施してください。")
        return ret, df_affinities
    
    # 親①-親②のメイン/サブ血統(基準値以下はスキップ)
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            for parent1_1 in lis_parent1_1:
                for parent2_1 in lis_parent2_1:
                    pp1 = lis_affinities_m_cp[ parent1_1 ][ parent2_1 ]
                    if pp1 < thresh_aff.th_ped1_pp:
                        continue
                    for parent1_2 in lis_parent1_2[parent1_1]:
                        for parent2_2 in lis_parent2_2[parent2_1]:
                            pp2 = lis_affinities_s_cp[ parent1_2 ][ parent2_2 ]
                            if pp2 < thresh_aff.th_ped2_pp:
                                continue
                            for cpg1_record in lis_affinities_cpg1[child1][child2][parent1_1][parent1_2]:
                                for cpg2_record in lis_affinities_cpg2[child1][child2][parent2_1][parent2_2]:
                                    affinity = pp1 + pp2 + cpg1_record[0] + cpg2_record[0]
                                    mark = get_mark(affinity)
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）
                                    lis_affinities.append([mark, affinity, 
                                                        cpg1_record[1], cpg1_record[2], 
                                                        cpg1_record[3], cpg1_record[4], 
                                                                        cpg2_record[2], 
                                                        cpg2_record[3], cpg2_record[4]] )

    # データフレーム型に変換してソート。
    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        write_log("候補0件。（他のログは出力しません。）")
        return ret, df_affinities

    df_affinities = pd.DataFrame( lis_affinities )
    df_affinities = df_affinities.sort_values([1, 2], ascending=[False, True])
    df_affinities.columns=['評価', '素相性値', '子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']
    
    ret = True

    return ret, df_affinities.reset_index()



# セッション系の初期化
def init_session_state(datalist):

    # ラジオボタンの選択結果保存領域作成
    if "radio_calc" not in st.session_state:
        st.session_state.radio_calc = RadioChoiceTable1.min_m十s式

    # ラジオボタンの選択結果保存領域作成
    if "radio_c" not in st.session_state:
        st.session_state.radio_c = RadioChoiceTable2.全モンスター
    if "radio_pg" not in st.session_state:
        st.session_state.radio_pg = RadioChoiceTable2.全モンスター
    if "radio_c_prev" not in st.session_state:
        st.session_state.radio_c_prev = RadioChoiceTable2.全モンスター
    if "radio_pg_prev" not in st.session_state:
        st.session_state.radio_pg_prev = RadioChoiceTable2.全モンスター

    # セレクトボックス選択結果保存域作成
    for i in range(datalist.num_monster):
        if f"select_ops_name{i}" not in st.session_state:
            st.session_state[f"select_ops_name{i}"] = ""
        elif f"select_ops_main{i}" not in st.session_state:
            st.session_state[f"select_ops_main{i}"] = ""
        elif f"select_ops_sub{i}" not in st.session_state:
            st.session_state[f"select_ops_sub{i}"] = ""

    # 全セレクトボックスの初期リスト設定
    if "select_options" not in st.session_state:
        st.session_state.select_options = [ [ 0 for j in range(datalist.num_monster) ] for i in range(datalist.num_kind)]
        for i in range(datalist.num_monster):
            st.session_state.select_options[0][i] = datalist.lis_mons_names
            st.session_state.select_options[1][i] = datalist.lis_main_ped
            st.session_state.select_options[2][i] = datalist.lis_sub_ped

    # 閾値設定箇所の有効/無効化フラグ
    if f"input_threshs_disabled" not in st.session_state:
        st.session_state.input_threshs_disabled = [False] * 8

    # 閾値関連の領域初期化
    for i in range(8):
        if f"input_thresh{i}" not in st.session_state:
            st.session_state[f"input_thresh{i}"] = 0
            entry_set_th(st.session_state.radio_calc.value)
    
    # 結果領域の初期化
    if f"df_affinities" not in st.session_state:
        st.session_state.df_affinities = pd.DataFrame()
    
    # 1回以上検索しているかどうかのフラグ
    if f"is_search_once_more" not in st.session_state:
        st.session_state.is_search_once_more = False

    return



# ラジオボタン作成関数
def create_radio_button(datalist):
    
    # テーブル選択結果格納場所の初期化
    datalist.lis_choice_table = [st.session_state.radio_c.value, st.session_state.radio_pg.value]
    
    # ラジオボタン作成
    datalist.lis_choice_table[0] = st.radio("子",      RadioChoiceTable2, horizontal=True, key="radio_c", on_change=radio_set_c_cmb_th, args=(datalist, ), help="検索時に使用する子のモンスター名テーブルを設定します。")
    datalist.lis_choice_table[1] = st.radio("親祖父母", RadioChoiceTable2, horizontal=True, key="radio_pg", on_change=radio_set_pg_cmb_th, args=(datalist, ), help="検索時に使用する親祖父母のモンスター名テーブルを設定します。")

    return


# セレクトボックス作成関数
def create_select_box(datalist):
    
    # ラベルの初期化
    lis_s_ops_labels = ['子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']

    # セレクトボックス作成
    for i in range(datalist.num_monster):
        col1, col2, col3 = st.columns(datalist.num_kind)
        with col1:
            datalist.lis_names[0][i] = st.selectbox(lis_s_ops_labels[i], st.session_state.select_options[0][i], index = 0, key=f'select_ops_name{i}', on_change=entry_set_th_from_cmb, args=(st.session_state.radio_calc.value, datalist), help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
            # datalist.lis_names[0][i] = st.selectbox(lis_s_ops_labels[i], st.session_state.select_options[0][i], index = 0, key=f'select_ops_name{i}', help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
        with col2:
            datalist.lis_names[1][i] = st.selectbox('メイン血統',         st.session_state.select_options[1][i], index = 0, key=f'select_ops_main{i}', on_change=select_set_ops, args=(datalist, i), help="モンスターのメイン血統を設定します。(絞込み用のため、不要なら設定不要。)")
        with col3:
            datalist.lis_names[2][i] = st.selectbox('サブ血統',           st.session_state.select_options[2][i], index = 0, key=f'select_ops_sub{i}', on_change=select_set_ops, args=(datalist, i), help="モンスターのメイン血統を設定します。(絞込み用のため、不要なら設定不要。)")
    
    return



# セレクトボックスの初期化
def reset_select_box(datalist):

    # モンスター名のコンボボックス参照リストの初期化
    radio_set_c_cmb_th(datalist, True)
    radio_set_pg_cmb_th(datalist, True)

    # コンボボックスの内容とか初期化
    for i in range(datalist.num_monster):
        datalist.lis_names[0][i] = ""
        datalist.lis_names[1][i] = ""
        datalist.lis_names[2][i] = ""
        st.session_state[f"select_ops_name{i}"] = ""
        st.session_state[f"select_ops_main{i}"] = ""
        st.session_state[f"select_ops_sub{i}"] = ""
        st.session_state.select_options[1][i] = datalist.lis_main_ped
        st.session_state.select_options[2][i] = datalist.lis_sub_ped

    return



# ログ領域への書き込み実施
def write_log(message):

    # 保存域の初期化
    if "log" not in st.session_state:
        st.session_state.log = ""
    
    # メッセージに追加
    st.session_state.log += message + "\n"

    return



# ログ領域のWeb上への表示
def print_log():
    
    txt = st.text_area("ログ情報", st.session_state.log, height=600, disabled=True, help="設定情報や検索時の途中経過について出力されます。")

    return



# ログ情報の初期化
def init_log():

    st.session_state.log = ""

    return


# 自端末へのログの保存
def save_log():
    pass


# 検索時に使用した各種値をログに出力する。
def set_log(Monster_info, lis_choice_table, thresh_aff):

    message_list1 = ['純血統+レア','全モンスター', '全モンスター(純血統のみ除く)']
    message_list2 = ["子", "親①", "祖父①", "祖母①", "親②", "祖父②", "祖母②"]

    # 参照テーブル
    write_log(f"◎モンスター参照テーブル：")
    write_log(f"　　　　　子：{message_list1[lis_choice_table[0].value]}")
    write_log(f"　　親祖父母：{message_list1[lis_choice_table[1].value]}")

    # 指定モンスター
    write_log(f"◎モンスター名：")
    for i, monster in enumerate(Monster_info):
        size1 = 10 - len(message_list2[i])
        if monster.name.startswith("("):
            size2 = 24 - len(monster.name)
        else:
            size2 = 22 - len(monster.name)
        size3 = 12 - len(monster.pedigree1)
        size4 = 12 - len(monster.pedigree2)
        write_log(f"{message_list2[i]:>{size1}}:{monster.name:>{size2}}, メイン：{monster.pedigree1:>{size3}}, サブ：{monster.pedigree2:>{size4}}")

    # 閾値
    write_log(f"◎相性値閾値：")
    write_log(f"　　a.子-親-祖父-祖母メイン血統の相性値閾値　　　　　　　　　　 ：{thresh_aff.th_ped1_cpg}")
    write_log(f"　　b.子-親-祖父-祖母サブ血統の相性値閾値　　　　　　　　　　　 ：{thresh_aff.th_ped2_cpg}")
    write_log(f"　　c.親①-親②メイン血統の相性値閾値　　　　　　　　　　　　　 ：{thresh_aff.th_ped1_pp}")
    write_log(f"　　d.親①-親②サブ血統の相性値閾値　　　　　　　　　　　　　　 ：{thresh_aff.th_ped2_pp}")
    write_log(f"　　e.子-親①間のメイン/サブ血統相性値合計閾値　　　　　　　　　：{thresh_aff.th_p1}")
    write_log(f"　　f.子-親②間のメイン/サブ血統相性値合計閾値　　　　　　　　　：{thresh_aff.th_p2}")
    write_log(f"　　g.親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{thresh_aff.th_cpg1}")
    write_log(f"　　h.親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値 ：{thresh_aff.th_cpg2}")

    return



def main():

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

    st.title("Sツール")
    st.write("Version 3.0.0a")


    #### 事前設定
    # 参照ファイル名の設定(配下でインスタンス変数を作成しているため注意。)
    ret, dic_file_names = set_input_filename()
    if not ret:
        return 

    # 付属データの読み込み/リストへの変換(配下でインスタンス変数を作成しているため注意。)
    datalist = read_all_data(dic_file_names)

    # モンスター名リストに主血統ID/副血統IDを相性表を元に追加
    ret = add_monster_id(datalist)
    if not ret:
        return 

    # セレクトボックス向けレアモンのレコードを追加
    add_raremon(datalist)

    # 読み込んだデータからリーグ表作成(配下でインスタンス変数を作成しているため注意。)
    create_league_table(datalist)

    # セレクトボックス用の初期リストの作成(配下でインスタンス変数を作成しているため注意。)
    create_combo_list(datalist)

    # セッション初期化
    init_session_state(datalist)


    # ラジオボタン作成
    st.write('')
    st.header('モンスター参照テーブル', help="子/親祖父母毎に検索で使用するテーブルを設定します。")
    create_radio_button(datalist)


    # リセット/セレクトボックスの作成
    st.write('')
    st.header('モンスター名設定', help="ここで検索したいモンスターの設定をします。全て空白でも検索可能ですが、相性値閾値設定次第で候補過多で出力されなくなるため注意。(メイン/サブ血統欄はモンスター名絞込み用の設定です。")
    if st.button('モンスター名選択リセット', help="選択済みのセレクトボックスの内容を初期化します。"):
        reset_select_box(datalist)
        create_select_box(datalist)
    else:
        create_select_box(datalist)


    # 詳細設定欄の作成
    st.write('')
    st.header('詳細設定')
    if st.checkbox("詳細に設定したい場合はチェックをつけてください。"):
        
        # 入力エリアの作成
        st.write('')
        st.subheader('相性値閾値設定', help="本項目での設定値未満の相性値の場合、検索候補から除外します。（よくわからない場合はそのままで問題なし。）")

        # 初期化した閾値を使用してテキストエリアを作成
        label_names = ["子-親-祖父-祖母メイン血統の相性値閾値", "子-親-祖父-祖母サブ血統の相性値閾値", 
                       "親①-親②メイン血統の相性値閾値", "親①-親②サブ血統の相性値閾値", 
                       "子-親①間のメイン/サブ血統相性値合計閾値", "子-親②間のメイン/サブ血統相性値合計閾値",
                       "親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値", 
                       "親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値"]
        
        # テキスト入力エリアを設定
        for i in range(len(label_names)):
            st.number_input(label_names[i], min_value=0, value=datalist.lis_threshs[i], key=f"input_thresh{i}", disabled=st.session_state.input_threshs_disabled[i])


    # 検索
    st.write('')
    st.header('検索')
    if st.button('検索開始！'):
        with st.spinner('processiong...'):
            ret = button_calc_affinity(datalist)
    

    # 結果の表示
    st.write('')
    st.header('検索結果', help="「検索開始！」ボタン押下後に設定値および結果が出力されます。")
    if st.session_state.is_search_once_more:
        print_log()
        st.dataframe(st.session_state.df_affinities, width=2000, height=500, use_container_width=True)
        # length = len(st.session_state.df_affinities.index) if len(st.session_state.df_affinities.index) < 10000 else 10000
        # st.dataframe(st.session_state.df_affinities.loc[0:length, :], width=2000, height=500)
    else:
        pass



# 呼び出し
if __name__ == '__main__':
    main()

