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
from lib.arrange_widget import init_page_setting



def main():

    # ページの初期設定
    init_page_setting("S Tool", "S Tool", "")
    st.subheader("- 補足 -")
    """
    &nbsp;
    """

    """
    ##### 相性の計算について  
    相性値の計算にあたって、有識者ましー様にご相談させていただきました。  
    また、過去の研究結果（オープンチャットに存在）や既存の一部ツールについてもご確認させていただきました。  
    これまで相性に関する研究を進んでされていた方々にこの場をお借りして感謝申し上げます。ありがとうございます。  

    以下は具体的な計算方法となります。  

    &nbsp;
    * **記号見方**  
      - M：主血統  
      - S：副血統  
      - A→B：AからみたBへの相性値  
      - min(A, B)：A, Bで小さいほうの値を採用  
      - 子、親、祖父、祖母：相性計算時に使用する登場人物  
      - ①：1人目の親と関連する親、祖父、祖母に対する記号  
      - ②：2人目の親と関連する親、祖父、祖母に対する記号  
    
    &nbsp;
    * **min(m)式**  
      以下のa~fの合計値が相性値(a～dは MorS/①or②の組合せ、e～fは親①②のM/S組合せ)  
      - a.①Mの子-親-祖父母間相性値  
        子M→親①M +  
        min(子M→祖父①M, 親①M→祖父①M) +  
        min(子M→祖母①M, 親①M→祖母①M)  
      - b.①Sの子-親-祖父母間相性値  
        子S→親①S +  
        min(子S→祖父①S, 親①S→祖父①S) +  
        min(子S→祖母①S, 親①S→祖母①S)  
      - c.②Mの子-親-祖父母間相性値  
        子M→親②M +  
        min(子M  →祖父②M, 親②M→祖父②M) +  
        min(子M  →祖母②M, 親②M→祖母②M)  
      - d.②Sの子-親-祖父母間相性値  
        子S→親②S +  
        min(子S  →祖父②S, 親②S→祖父②S) +  
        min(子S  →祖母②S, 親②S→祖母②S)
      - e.①②Mの親間相性値  
        親①M→親②M  
      - f.①②Sの親間相性値
        親①S→親②S
    
    &nbsp;
    * **min(m+s)式**  
      以下のa~cの合計値が相性値。
      - a.①の子-親-祖父母間相性値  
        子M→親①M +  
        子S→親①S +  
        min( (子M→祖父①M) + (子S→祖父①S), (親①M→祖父①M) + (親①S→祖父①S) ) +  
        min( (子M→祖母①M) + (子S→祖母①S), (親①M→祖母①M) + (親①S→祖母①S) )  
      - b.②の子-親-祖父母間相性値  
        子M→親②M +  
        子S→親②S +  
        min( (子M→祖父②M) + (子S→祖父②S), (親②M→祖父②M) + (親②S→祖父②S) ) +  
        min( (子M→祖母②M) + (子S→祖母②S), (親②M→祖母②M) + (親②S→祖母②S) )
      - c.①②の親間相性値  
        親①M→親②M +  
        親①S→親②S
    
    &nbsp;
    * **レアモンの扱いについて**  
      レアが含まれる組み合わせの場合、以下のように計算されるため注意。  
      A→Bにおいて… 
      | A | B | 相性値 |
      |:--|:--|--:| 
      | レアモン | レアモン | 32 |
      | レアモン | レアモン以外 | 16 |
      | レアモン以外 | レアモン | 32 |
      | レアモン以外 | レアモン以外 | 各モンスターの相性表を確認 |  

      ※ 相性値は大きいほど相性が良いことを示します。  

    &nbsp;
    &nbsp;
    &nbsp;
    ##### 相性の基準について  
    以下の基準で相性値に記号を付与しています。  
      | 記号 | 相性値 |
      |:--|:--:| 
      | × | 0 ～ 257 |
      | △ | 257.1 ～ 374 |
      | 〇 | 374.1 ～ 490 |
      | ◎ | 490.1 ～ 610 |
      | ☆ | 610.1 ～  |
    
    なお、実際のゲーム上では±20程度の誤差が発生するとされています。
    
    """


# 呼び出し
if __name__ == '__main__':
    main()


