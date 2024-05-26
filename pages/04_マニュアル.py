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
    
    st.title("マニュアル -作成中-")



# 呼び出し
if __name__ == '__main__':
    main()
