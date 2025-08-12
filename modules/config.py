# --- modules/config.py ---

import streamlit as st

def setup_page(title="永傳《影響力》傳承規劃平台", icon_path="logo.png", layout="centered"):
    """
    統一設定 Streamlit 頁面樣式：
    - title：頁面標題
    - icon_path：標籤頁圖示（支援圖檔或 emoji）
    - layout：'centered' 或 'wide'
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon_path,
        layout=layout
    )
