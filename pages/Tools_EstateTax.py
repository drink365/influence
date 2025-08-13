# pages/Tools_EstateTax.py
# 遺產稅試算頁面（呼叫 UI 模組）
import streamlit as st
from legacy_tools.modules.estate_tax_ui import render_estate_tax_page

# 直接呼叫
render_estate_tax_page()
