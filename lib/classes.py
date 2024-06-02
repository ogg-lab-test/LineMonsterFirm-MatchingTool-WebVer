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

import pandas as pd



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



# データをまとめるクラス(サーバ全体で1つだけ持つ。)
class DataList():

    ### 各種設定値
    # 数式の選択結果
    choice_exp1 = 1
    choice_exp2 = 2
    # モンスター参照テーブル参照結果の個数
    num_choice_table_result = 2
    # モンスター参照テーブル参照結果の選択肢
    choice_table_org = 1
    choice_table_all = 2
    choice_table_ex_org = 3
    # モンスター名設定欄の枠の数
    num_monster = 7
    num_kind = 3
    # 相性閾値設定欄
    num_threshs = 8
    # 検索候補最大数
    N1 = 50000
    N2 = 50000
    N3 = 1500000
    # 最大通知結果数、メモリ使用量
    max_result_num = 4999 # +1されるため注意
    max_memory_size = 800.0

    def __init__(self):

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

        # コンボリスト用リスト/DF(create_combo_list参照)
        self.lis_main_ped = []
        self.lis_sub_ped = []
        self.lis_mons_names = []

        self.df_monsters_org = pd.DataFrame()
        self.lis_mons_names_org = []
        
        self.df_monsters_ex_org = pd.DataFrame()
        self.lis_mons_names_ex_org = []

        # 相性閾値の初期値設定用リスト(起動直後のみ、それ以降は使用しない。)
        self.lis_threshs = [0, 0, 34, 32, 75, 75, 75, 75]



# データをまとめるクラス(セッションごとに1つもつ)
class SessionDataList():
    def __init__(self):

        # モンスター参照用のリーグ表(子、親用)
        self.lis_mons_league_tb_c       = [[]]
        self.lis_mons_league_tb_pg      = [[]]

        # ラジオボタン選択結果(テーブル情報)保存用格納域
        self.lis_choice_table = [0] * DataList.num_choice_table_result

        # コンボリスト用DF（子、親用）
        self.df_monsters_c = pd.DataFrame()
        self.df_monsters_pg = pd.DataFrame()

        # 検索用名前格納用リスト
        self.lis_names = [ [ "" for j in range(DataList.num_monster) ] for i in range(DataList.num_kind)]

        # 結果一時格納用の場所
        self.df_affinities       = pd.DataFrame( [] )


