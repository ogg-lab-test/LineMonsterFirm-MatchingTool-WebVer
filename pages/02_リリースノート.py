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

    init_page_setting("S Tool", "S Tool", "")
    st.subheader("- リリースノート -")
    """
    &nbsp;
    """

    """
    - **2024/05/02：Version 1.1.0**  
      Windows版相性計算ツールをリリース。(現在公開停止中。)

    - **2024/05/19：Version 2.0.1**  
      Windows版相性計算ツールの不具合等を修正。(ダウンロードは[こちら](https://github.com/sean-sheep1/LineMonsterFirm-MatchingTool-LocalVer ""))  
      ただし、更新停止中。
    
    - **2024/06/02：Version 3.0.0**  
      Windows版相性計算ツールをWebアプリ化。  
      ☆キジン種については未対応のため注意。
    """



# 呼び出し
if __name__ == '__main__':
    main()


