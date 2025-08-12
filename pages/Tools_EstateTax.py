import streamlit as st
from legacy_tools.modules.estate_tax_ui import render_estate_tax_page

st.set_page_config(page_title="遺產稅試算｜influence9", page_icon="🧮", layout="wide")
render_estate_tax_page()