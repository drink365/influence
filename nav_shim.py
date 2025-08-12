# pages/nav_shim.py
# Safe shim for goto(): prefer src.utils.nav.goto, fallback to simple switch_page.

def goto_fallback(st, script_path_or_name: str, fallback_label: str | None = None):
    try:
        st.switch_page(script_path_or_name)
    except Exception:
        st.error(f"找不到頁面：{script_path_or_name}")

try:
    from nav_shim import goto as _goto
    goto = _goto
except Exception:
    goto = goto_fallback
