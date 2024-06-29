"""
   Copyright 2024/6/29 sean of copyright owner

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
import os

# 自作ライブラリ等
from lib.classes import DataList



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
    df_temp = df_monsters[df_monsters["モンスター名"].str.startswith('（●レア）')]
    name_list_raremon_m = df_temp.iloc[:, 1].to_list()

    # レアモンタグのついたレコードの主血統名のリスト内に、比較用リストの名前がない場合に仮インデックスでレコードを追加
    for i, name in enumerate(name_list_m_row):
        if name not in name_list_raremon_m:
            df_monsters.loc[f'temp{i}'] = [f'（●レア）{name}', name, 'レア', i+1, 0]
    
    # モンスター名のファイルのみソート
    # df_monsters = df_monsters.sort_values(['主血統ID', 'モンスター名'], ascending=[True, True])
    df_monsters = df_monsters.sort_values(['モンスター名'], ascending=[True])

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
# 　　　→SessionDataListに個別のデータを持つようにすること。
def create_league_table(datalist):
    
    # モンスター名リストをlistに変換
    lis_monsters = datalist.df_monsters.values.tolist()

    # リーグ表用のリストの初期化
    length = len(datalist.lis_affinities_m_cp)
    lis_mons_league_tb_all       = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_ex_org    = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_org       = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_only_org  = [[ "-" for i in range(length)] for i in range(length)]
    lis_mons_league_tb_only_rare = [[ "-" for i in range(length)] for i in range(length)]
    
    # レアモンスター用の変数（血統ID、名前保存場所）
    num_rare = 0
    name_rare = "（●レア）"  # "（●レア）"とついたモンスター名を保存する場所。

    # モンスター名リスト → リーグ表に変換
    for row in lis_monsters:
        if lis_mons_league_tb_all[row[3]][row[4]] == "-":
            if row[0].startswith(name_rare):
                # タグ用のレアモンスター名があってもリーグ表には追加しない。
                continue
            if row[4] == num_rare:
                lis_mons_league_tb_all[row[3]][row[4]]       = name_rare + row[1]
                lis_mons_league_tb_ex_org[row[3]][row[4]]    = name_rare + row[1]
                lis_mons_league_tb_org[row[3]][row[4]]       = name_rare + row[1]
                lis_mons_league_tb_only_rare[row[3]][row[4]] = name_rare + row[1]
            else:
                lis_mons_league_tb_all[row[3]][row[4]]     = row[0]
                lis_mons_league_tb_ex_org[row[3]][row[4]]  = row[0]
                
        if row[3] == row[4]:
            lis_mons_league_tb_ex_org[row[3]][row[4]]     = "-"
            lis_mons_league_tb_org[row[3]][row[4]]        = row[0]
            lis_mons_league_tb_only_org[row[3]][row[4]]   = row[0]
    
    # 設定
    datalist.lis_mons_league_tb_all       = lis_mons_league_tb_all
    datalist.lis_mons_league_tb_ex_org    = lis_mons_league_tb_ex_org
    datalist.lis_mons_league_tb_org       = lis_mons_league_tb_org
    datalist.lis_mons_league_tb_only_org  = lis_mons_league_tb_only_org
    datalist.lis_mons_league_tb_only_rare = lis_mons_league_tb_only_rare

    # debug start
    # temp1 = pd.DataFrame(datalist.lis_mons_league_tb_ex_org)
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
    datalist.df_monsters_org = df_monsters[(df_monsters["主血統"] == df_monsters["副血統"]) | (df_monsters["モンスター名"].str.startswith('（●レア）'))].copy()
    datalist.lis_mons_names_org = datalist.df_monsters_org.iloc[:, 0].to_list()
    datalist.lis_mons_names_org.insert(0, "")

    # 主血統のみ除く全モンスター名リスト
    datalist.df_monsters_ex_org = df_monsters[df_monsters["主血統"] != df_monsters["副血統"]].copy()
    datalist.lis_mons_names_ex_org = datalist.df_monsters_ex_org.iloc[:, 0].to_list()
    datalist.lis_mons_names_ex_org.insert(0, "")

    # 主血統のみの全モンスター名リスト
    datalist.df_monsters_only_org = df_monsters[df_monsters["主血統"] == df_monsters["副血統"]].copy()
    datalist.lis_mons_names_only_org = datalist.df_monsters_only_org.iloc[:, 0].to_list()
    datalist.lis_mons_names_only_org.insert(0, "")

    # レアモンのみの全モンスター名リスト
    datalist.df_monsters_only_rare = df_monsters[(df_monsters["モンスター名"].str.startswith('（●レア）'))].copy()
    datalist.lis_mons_names_only_rare = datalist.df_monsters_only_rare.iloc[:, 0].to_list()
    datalist.lis_mons_names_only_rare.insert(0, "")

    # 検索候補削除用のリスト
    datalist.df_monsters_del = df_monsters[(df_monsters["副血統"] != "レア") | df_monsters["モンスター名"].str.startswith('（●レア）')].copy()
    datalist.lis_mons_names_del = datalist.df_monsters_del.iloc[:, 0].to_list()

    # 変数をdatalistに格納
    datalist.df_monsters = df_monsters

    return



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



# サーバ全体での初期処理
@st.cache_resource
def init_datalist_for_all_client():

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

    # 保存領域に設定
    st.session_state.datalist = datalist

    return datalist


