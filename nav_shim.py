# nav_shim.py（穩定導頁，含參數版本）
def goto_fallback(st, script_path_or_name: str, fallback_label: str | None = None):
    try:
        st.switch_page(script_path_or_name)
    except Exception:
        st.error(f"找不到頁面：{script_path_or_name}")

def goto_with_params_fallback(st, script_path_or_name: str, **params):
    # 嘗試設置查詢參數（不同版本 Streamlit API 名稱略有差異）
    try:
        st.query_params.clear()
        if params:
            st.query_params.update(params)
    except Exception:
        try:
            st.experimental_set_query_params(**params)
        except Exception:
            pass
    try:
        st.switch_page(script_path_or_name)
    except Exception:
        st.error(f"找不到頁面：{script_path_or_name}")

try:
    from src.utils.nav import goto as _goto
    goto = _goto
except Exception:
    goto = goto_fallback

try:
    from src.utils.nav import goto_with_params as _goto_with_params
    goto_with_params = _goto_with_params
except Exception:
    goto_with_params = goto_with_params_fallback
