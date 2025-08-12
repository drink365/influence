import sys, os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from legacy_tools.modules.estate_tax_ui import render_estate_tax_page

st.set_page_config(page_title="遺產稅試算｜influence9", page_icon="🧮", layout="wide")
render_estate_tax_page()