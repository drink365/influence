# pages/0_AI_Copilot_Pro.py
# AI Copilot Pro：永傳家族辦公室專屬 AI 顧問（單頁控制、品牌化輸出）
from __future__ import annotations

import streamlit as st
from datetime import datetime
from typing import List, Dict

from legacy_tools.modules.pdf_generator import generate_pdf

# -------------------------------------------------
# 頁面設定（預設收起側欄，避免誤會控制在側邊）
# -------------------------------------------------
st.set_page_config(
    page_title="AI Copilot Pro｜永傳家族辦公室",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 品牌化 System Prompt（專屬：永傳家族辦公室）
# -------------------------------------------------
def build_system_prompt(
    tone: str, audience: str, purpose: str, fmt: str, length: str,
    add_brand: bool, keywords: str, avoid: str
) -> str:
    # 語氣、長度、格式說明
    tone_map = {
        "溫暖專業": "溫暖、具同理心，但用字精確且有專業感；避免誇張與行話。",
        "精準中性": "中性、冷靜、直達重點；避免形容詞與冗語。",
        "權威簡潔": "權威、簡潔、結構化；先結論、後理由。",
        "故事引導": "用精簡故事切入，帶出問題與解法，最後收斂行動建議。",
        "簡報要點": "每點 10–20 字，像投影片重點；不贅述。",
    }
    want_len = {"短": "約 80–150 字", "中": "約 150–300 字", "長": "約 300–600 字"}[length]
    fmt_hint = "請用條列格式（短句、每點一行）" if fmt == "條列重點" else "請用流暢段落敘述、段落短而清楚"

    kw = f"必須包含關鍵詞：{keywords}。" if keywords.strip() else ""
    ban = f"避免出現：{avoid}。" if avoid.strip() else ""
    brand_sig = "結尾附：永傳家族辦公室｜www.gracefo.com｜123@gracefo.com。" if add_brand else "結尾不需品牌簽名。"

    # 專業框架（台灣市場；單位：萬元 TWD）
    domain_knowledge = """
你是「永傳家族辦公室」的資深顧問，服務高資產家族，整合保險、法律與稅務，重視合規與風險控管。
台灣常用參數（僅作語言與脈絡，不作精算保證）：
- 遺產稅：免稅額 1,333 萬，喪葬費 138 萬，配偶 553 萬，子女/祖父母/兄弟姊妹 56 萬，父母 138 萬，重度身心障礙 693 萬；稅率級距常見為 10%/15%/20%。
- 保單策略：定期壽險（風險保障/稅源預留）、終身壽險（確定性傳承/現金價值）、美元/台幣保單（幣別配置與匯率風險），合理的前期加保須視繳費年期與資金流規劃；避免誇大或保證。
- 單位以「萬元（TWD）」表達；若有外幣，說明等值概念與風險。
回覆原則：合規、透明、可落地。先重點，再作法，最後下一步行動（CTA）。
避免：保證詞、超收益承諾、未經證實的稅務結論。
"""

    return (
        f"{domain_knowledge}\n\n"
        f"受眾：{audience}。目標：{purpose}。語氣：{tone_map.get(tone, tone)}。\n"
        f"{fmt_hint}，篇幅 {want_len}。{kw}{ban} {brand_sig}\n"
        "請使用繁體中文，讓非專業者也能看懂。必要時用簡單例子輔助。"
    )

# -------------------------------------------------
# 嘗試使用 OpenAI；無金鑰時採柔性離線提示
# -------------------------------------------------
def llm_generate(prompt: str, system: str, mode: str = "normal") -> str:
    """
    mode: normal / shorter / longer / slide
    """
    try:
        import openai  # type: ignore
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            instruction = {
                "normal": "請依系統要求與使用者內容，產出最佳版本。",
                "shorter": "請在保留關鍵資訊下，改寫為更精簡版本（約 60–120 字）。",
                "longer": "請擴寫為更完整版本（約 250–500 字），補足背景與行動建議。",
                "slide": "請轉為『簡報大綱』：每點一行、用詞精煉、可直接放投影片。",
            }[mode]
            msgs = [
                {"role": "system", "content": system},
                {"role": "user", "content": f"{instruction}\n\n使用者內容：\n{prompt}"},
            ]
            # 可視需要調整模型
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=msgs,
                temperature=0.6 if mode != "slide" else 0.3,
                max_tokens=1200,
            )
            return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    # ---- 柔性離線提示（不顯示「離線草稿」字眼）----
    tag = {"normal":"建議版本","shorter":"精簡版本","longer":"擴寫版本","slide":"簡報大綱"}[mode]
    hint = "（目前為暫時版本；連線完成後將提供即時 AI 專業建議。）"
    if mode == "slide":
        body = [
            f"【{tag}】{hint}",
            "• 問題/情境：請簡述你當前的關注點與家族目標",
            "• 核心觀念：預留稅源、確定性傳承、現金流安全邊界",
            "• 主要做法：分階段配置、適度保單加保、重要里程碑檢視",
            "• 下一步：先產出資產地圖/稅試算 → 預約諮詢",
        ]
    else:
        body = [
            f"【{tag}】{hint}",
            "重點：以你的情境為核心，先結論後方法，避免行話；必要時補充例子。",
            "內容草稿：",
            prompt or "（尚未輸入內容）",
        ]
    return "\n".join(body)

# -------------------------------------------------
# Header：客戶視角說明
# -------------------------------------------------
st.markdown("""
<div style="background:#f5f8ff;padding:1.25rem 1.25rem;border-radius:12px;border:1px solid #e2e8f0;">
  <h2 style="margin:0 0 .5rem 0;color:#0f172a;">你的專屬 AI 規劃助理，讓傳承更清楚、更從容</h2>
  <p style="margin:0;color:#334155;">
    把法律、稅務與保險的複雜度變簡單。用對話，就能快速產出藍圖、簡報摘要與下一步建議。
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# 控制區（放在頁面上方）
# -------------------------------------------------
st.markdown("### ✍️ 寫作控制")
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1:
    tone = st.selectbox("語氣", ["溫暖專業", "精準中性", "權威簡潔", "故事引導", "簡報要點"], index=0)
with c2:
    audience = st.selectbox("受眾", ["家族客戶", "企業主", "專業夥伴", "一般大眾"], index=0)
with c3:
    purpose = st.selectbox("目的", ["諮詢回覆", "企劃摘要", "簡報大綱", "社群貼文", "Email 正文"], index=1)
with c4:
    fmt = st.radio("格式", ["條列重點", "段落敘述"], index=0, horizontal=True)

c5, c6, c7 = st.columns([1, 1, 1])
with c5:
    length = st.select_slider("長度", options=["短", "中", "長"], value="中")
with c6:
    add_brand = st.checkbox("加入品牌簽名（永傳家族辦公室）", value=True)
with c7:
    st.caption("金額單位以 **萬元（TWD）** 為主；你也可以把工具的數據貼到下方再重寫。")

c8, c9 = st.columns([1, 1])
with c8:
    keywords = st.text_input("必含關鍵詞（逗號分隔）", value="")
with c9:
    avoid = st.text_input("避免詞（逗號分隔）", value="")

st.markdown("---")

# -------------------------------------------------
# 主區：輸入 / 產出
# -------------------------------------------------
col_in, col_out = st.columns([1, 1.2], gap="large")

with col_in:
    st.markdown("#### 📝 你的情境或指示")
    user_prompt = st.text_area(
        "請描述你要產出的內容（可貼上工具結果、客戶背景、限制條件）",
        height=220,
        placeholder="範例：幫我寫一段簡報開場，說明為何要預留稅源，語氣溫暖專業，200 字內…"
    )
    generate_btn = st.button("✨ 產出內容", type="primary", use_container_width=True)

    st.markdown("##### 快捷重寫")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        shorter_btn = st.button("更精簡")
    with col_b:
        longer_btn = st.button("更完整")
    with col_c:
        slide_btn = st.button("轉成簡報大綱")

# 狀態
if "copilot_output" not in st.session_state:
    st.session_state.copilot_output = ""

# 產出
system_prompt = build_system_prompt(tone, audience, purpose, fmt, length, add_brand, keywords, avoid)

with col_out:
    st.markdown("#### 🧾 產出結果")
    if generate_btn and not user_prompt.strip():
        st.warning("請先輸入內容或情境，再按「產出內容」。")
    if generate_btn and user_prompt.strip():
        st.session_state.copilot_output = llm_generate(user_prompt, system_prompt, mode="normal")

    if st.session_state.copilot_output and shorter_btn:
        st.session_state.copilot_output = llm_generate(st.session_state.copilot_output, system_prompt, mode="shorter")
    if st.session_state.copilot_output and longer_btn:
        st.session_state.copilot_output = llm_generate(st.session_state.copilot_output, system_prompt, mode="longer")
    if st.session_state.copilot_output and slide_btn:
        st.session_state.copilot_output = llm_generate(st.session_state.copilot_output, system_prompt, mode="slide")

    result = st.text_area("", value=st.session_state.copilot_output, height=420)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "下載 .txt",
            data=(result or "").encode("utf-8"),
            file_name=f"AI_Copilot_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not result.strip()
        )
    with col_dl2:
        if st.button("下載 PDF", use_container_width=True, disabled=not result.strip()):
            pdf_bytes = generate_pdf(
                content=result,
                title=f"{purpose}",
                logo_path=None,  # 不傳也會自動抓根目錄 logo.png
                footer_text="永傳家族辦公室｜www.gracefo.com｜123@gracefo.com",
            ).getvalue()
            st.download_button(
                "點此下載 PDF",
                data=pdf_bytes,
                file_name=f"AI_Copilot_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

st.markdown("---")
# 導覽（名稱依你的偏好：只有資產地圖保留「家族」二字）
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    st.page_link("pages/Tools_AssetMap.py", label="🗺️ 家族資產地圖")
with col_nav2:
    st.page_link("pages/Tools_EstateTax.py", label="🧮 遺產稅試算")
with col_nav3:
    st.page_link("pages/Tools_InsuranceStrategy.py", label="📦 保單策略建議")
