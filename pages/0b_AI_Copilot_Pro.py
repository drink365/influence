# pages/0b_AI_Copilot_Pro.py
# 🪄 AI 行銷助手 Pro（免 API）
# 多模板＋口吻庫（商周／今周刊／TED／暖專）＋品牌簽名、自動 Hashtag、字數與 emoji 控制
import streamlit as st
from datetime import date

st.set_page_config(page_title="AI 行銷助手 Pro（免 API）", page_icon="🪄", layout="wide")
st.title("🪄 AI 行銷助手 Pro（免 API）")
st.caption("輸入重點 → 一鍵生成 FB 貼文 / LINE 私訊 / 演講開場（含商周／今周刊／TED 口吻模板）。不需 API。")

# -----------------------------
# 控制面板
# -----------------------------
with st.form("mk_pro"):
    c1, c2, c3 = st.columns(3)
    with c1:
        audience = st.selectbox("🎯 目標受眾", ["企業主", "高資產家庭", "年輕上班族", "一般家庭"], index=0)
        channel = st.selectbox("📤 產出格式", ["Facebook 貼文", "LINE 私訊", "演講開場"], index=0)
        persona = st.selectbox("🗣️ 口吻模板", ["暖專（Grace風格）", "商周風", "今周刊風", "TED 演說風"], index=0)
    with c2:
        topic = st.text_input("🧩 主題 / 服務", "傳承規劃")
        key_points = st.text_area("📌 關鍵重點（每行一點）", "1. 有數據與圖像化工具\n2. 可先做風險盤點\n3. 提供預約諮詢")
        cta = st.text_input("👉 CTA 呼籲動作", "私訊我，預約 30 分鐘諮詢")
    with c3:
        brand = st.text_input("🏷️ 品牌簽名（可留空）", "永傳家族辦公室｜影響力傳承計畫")
        max_len = st.slider("✂️ 建議字數上限", 80, 500, 220, step=10)
        with_emoji = st.toggle("🙂 適量加入 Emoji", value=True)

    preset = st.radio("⚡ 快速模板", ["自訂輸入", "稅源預留（高資產）", "壯世代轉型（行銷）", "企業主接班（家業/家產/家風）"], index=0)

    submitted = st.form_submit_button("✨ 產生內容")

# -----------------------------
# 工具函式
# -----------------------------
def bullets(text: str):
    return [s.strip(" 　-•\t1234567890.).、") for s in text.splitlines() if s.strip()]

def apply_preset(preset_name: str, topic: str, pts: list[str], cta: str):
    if preset_name == "稅源預留（高資產）":
        topic = "稅源預留與保單流動性"
        pts = ["先算清楚遺產稅缺口，別讓孩子被動賣資產",
               "用保單做流動性與公平性，避免手足糾紛",
               "傳承地圖＋遺產稅試算，提案一目了然"]
        cta = "想知道你家的缺口？我用 30 分鐘帶你看懂。"
    elif preset_name == "壯世代轉型（行銷）":
        topic = "壯世代的 AI 行銷與成交升級"
        pts = ["用模板＋工具，少走彎路、快速啟動個人品牌",
               "FB/LINE/開場白一鍵生成，免寫手也能上線",
               "先上場、再優化：3 週做出第一波引流"]
        cta = "報名 2 週實戰班，讓我們陪你第一波上線。"
    elif preset_name == "企業主接班（家業/家產/家風）":
        topic = "企業接班三軸：家業/家產/家風"
        pts = ["家業：治理與權責設計，避免戲劇化接班",
               "家產：信託＋保單流動性，降低稅務與爭議",
               "家風：價值與故事保留下來，才有長遠"]
        cta = "想看你的接班藍圖？我用案例與工具帶你走一遍。"
    return topic, pts, cta

def style_persona(text: str, persona: str, with_emoji: bool) -> str:
    """根據口吻模板微調語氣與節奏。"""
    if persona == "商周風":
        text = (text.replace("我們", "企業")
                    .replace("你", "企業主")
                    .replace("可以", "能")
                    .replace("會", "將"))
        add = "\n（重點是：用數據與制度降低不確定性，建立長期競爭力。）"
        text += add
    elif persona == "今周刊風":
        text += "\n\n— 重點不在『多做什麼』，而是『先做對的事，再把事情做對』。"
    elif persona == "TED 演說風":
        text = "讓我先說一個故事。\n\n" + text + "\n\n今天，我想留給大家一個行動：從一個小小的決定開始。"
    else:
        # 暖專（Grace風格）
        text = text.replace("客戶", "家人").replace("產品", "工具").replace("服務", "陪伴")
    if with_emoji:
        text += "\n" + "🌱" + " " + "一起把重要的事，做得更踏實。"
    return text

def limit_length(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    # 簡單裁切到最近的句號或換行
    cut = text[:max_len]
    for sep in ["\n", "。", "！", "!", "？", "?"]:
        if sep in cut[::-1]:
            idx = cut.rfind(sep)
            if idx > 0:
                return cut[:idx+1] + " …"
    return cut + " …"

def hash_brand(brand: str) -> str:
    if not brand.strip():
        return ""
    tags = [s for s in brand.replace("｜", " ").replace("、", " ").split() if s.strip()]
    return "#" + " #".join(tags)

# -----------------------------
# 產生模板
# -----------------------------
def gen_fb(aud, topic, pts, cta, brand):
    title = f"【{topic}｜{aud}不可不知】"
    head = f"你是否也在想：{pts[0] if pts else '如何更有效把傳承做對？'}"
    lines = [title, head, ""]
    lines += [f"・{p}" for p in pts]
    lines += ["", f"👉 {cta}"]
    hb = hash_brand(brand)
    if hb:
        lines += ["", hb]
    return "\n".join(lines)

def gen_line(aud, topic, pts, cta):
    lines = [f"{aud}您好，我是 Grace。這裡是「{topic}」的重點整理："]
    lines += [f"• {p}" for p in pts]
    lines += ["", f"如果您方便，我可以用 15–30 分鐘把做法講清楚。{cta}"]
    return "\n".join(lines)

def gen_opening(aud, topic, pts):
    lines = [f"各位好，今天我們談「{topic}」。"]
    lines += [f"多數{aud}會遇到："]
    for i, p in enumerate(pts[:3] if pts else ["資訊分散難比較", "稅務流動性不足", "家族對話卡關"], 1):
        lines += [f"{i}. {p}"]
    lines += ["今天我們用案例與工具，帶大家看一條可複製的路。"]
    return "\n".join(lines)

# -----------------------------
# 產出流程
# -----------------------------
if submitted:
    pts = bullets(key_points)

    # 套用快速模板
    if preset != "自訂輸入":
        topic, pts, cta = apply_preset(preset, topic, pts, cta)

    if channel == "Facebook 貼文":
        out = gen_fb(audience, topic, pts, cta, brand)
    elif channel == "LINE 私訊":
        out = gen_line(audience, topic, pts, cta)
    else:
        out = gen_opening(audience, topic, pts)

    # 依口吻調校
    out = style_persona(out, persona, with_emoji)
    # 字數控制
    out = limit_length(out, max_len)

    st.markdown("### ✍️ 產出結果")
    st.code(out, language="markdown")
    st.download_button("下載為 .txt", data=out, file_name=f"mkPRO_{date.today()}.txt")

st.markdown("---")
st.caption("備註：此頁為『免 API』範例。若要導入自家用語庫、案例庫與提案模板，可加一層參數檔或接入 OpenAI API。")
