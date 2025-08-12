# pages/0b_AI_Copilot_Pro.py
# 🪄 AI 行銷助手 Pro（免 API）＋ brand.json
# 讀取根目錄 brand.json：brand_quotes / hashtags / persona_keywords / default_brand_signature
import streamlit as st
from datetime import date
import os, json, random

st.set_page_config(page_title="AI 行銷助手 Pro（品牌金句＋Hashtag）", page_icon="🪄", layout="wide")
st.title("🪄 AI 行銷助手 Pro")
st.caption("輸入重點 → 一鍵生成 FB 貼文 / LINE 私訊 / 演講開場。自動讀取 brand.json 的金句與 Hashtag。")

# -----------------------------
# 讀取 brand.json（根目錄）
# -----------------------------
def load_brand_config():
    # 尋找專案根目錄的 brand.json
    # 這個檔案應與 app.py 同層（repo 根）
    try_paths = []
    # 1) 以此檔案所在路徑向上兩層嘗試
    this_dir = os.path.dirname(__file__)
    try_paths.append(os.path.abspath(os.path.join(this_dir, "..", "brand.json")))
    try_paths.append(os.path.abspath(os.path.join(this_dir, "..", "..", "brand.json")))
    # 2) 以當前工作目錄嘗試（Streamlit 通常為 repo 根）
    try_paths.append(os.path.abspath(os.path.join(os.getcwd(), "brand.json")))
    for p in try_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    # 安全預設
    return {
        "brand_name": "永傳家族辦公室",
        "slogan": "傳承您的影響力",
        "brand_quotes": [
            "財富是工具，傳承是使命；把愛與價值留得更久。"
        ],
        "hashtags": ["#家族傳承", "#保單策略"],
        "persona_keywords": {
            "Grace": ["溫暖", "專業", "清楚", "可落地"],
            "商周": ["策略", "趨勢", "紀律"],
            "今周刊": ["財經脈絡", "務實", "方法論"],
            "TED": ["故事", "洞見", "行動呼籲"]
        },
        "default_brand_signature": "永傳家族辦公室｜影響力傳承計畫"
    }

CFG = load_brand_config()

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
        brand = st.text_input("🏷️ 品牌簽名（可留空）", CFG.get("default_brand_signature", ""))
        max_len = st.slider("✂️ 建議字數上限", 80, 500, 220, step=10)
        with_emoji = st.toggle("🙂 適量加入 Emoji", value=True)

    preset = st.radio("⚡ 快速模板", ["自訂輸入", "稅源預留（高資產）", "壯世代轉型（行銷）", "企業主接班（家業/家產/家風）"], index=0)
    use_quote = st.toggle("🧡 自動插入品牌金句", value=True)
    use_hashtags = st.toggle("🏷️ 自動插入品牌 Hashtag", value=True)

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
    if persona == "商周風":
        text = (text.replace("我們", "企業")
                    .replace("你", "企業主")
                    .replace("可以", "能")
                    .replace("會", "將"))
        text += "\n（重點：用數據與制度降低不確定性，建立長期競爭力。）"
    elif persona == "今周刊風":
        text += "\n\n— 重點不在『多做什麼』，而是『先做對的事，再把事情做對』。"
    elif persona == "TED 演說風":
        text = "讓我先說一個故事。\n\n" + text + "\n\n今天，我想留給大家一個行動：從一個小小的決定開始。"
    else:
        text = text.replace("客戶", "家人").replace("產品", "工具").replace("服務", "陪伴")
    if with_emoji:
        text += "\n🌱 一起把重要的事，做得更踏實。"
    return text

def limit_length(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    for sep in ["\n", "。", "！", "!", "？", "?"]:
        if sep in cut[::-1]:
            idx = cut.rfind(sep)
            if idx > 0:
                return cut[:idx+1] + " …"
    return cut + " …"

def hash_brand(brand_tags: list[str]) -> str:
    tags = [s.strip() for s in (brand_tags or []) if s.strip()]
    return "" if not tags else "#" + " #".join(tags)

def pick_brand_quote(cfg: dict) -> str:
    arr = cfg.get("brand_quotes", [])
    return random.choice(arr) if arr else ""

# -----------------------------
# 產生模板
# -----------------------------
def gen_fb(aud, topic, pts, cta, brand_sig, cfg, use_quote, use_hashtags):
    title = f"【{topic}｜{aud}不可不知】"
    head = f"你是否也在想：{pts[0] if pts else '如何更有效把傳承做對？'}"
    lines = [title, head, ""]
    lines += [f"・{p}" for p in pts]
    if use_quote:
        q = pick_brand_quote(cfg)
        if q:
            lines += ["", f"💡 {q}"]
    lines += ["", f"👉 {cta}"]
    if brand_sig:
        lines += ["", brand_sig]
    if use_hashtags:
        hb = hash_brand(cfg.get("hashtags", []))
        if hb:
            lines += ["", hb]
    return "\n".join(lines)

def gen_line(aud, topic, pts, cta, cfg, use_quote):
    lines = [f"{aud}您好，我是 Grace。這裡是「{topic}」的重點整理："]
    lines += [f"• {p}" for p in pts]
    if use_quote:
        q = pick_brand_quote(cfg); 
        if q: lines += ["", f"💡 {q}"]
    lines += ["", f"如果您方便，我可以用 15–30 分鐘把做法講清楚。{cta}"]
    return "\n".join(lines)

def gen_opening(aud, topic, pts, cfg, use_quote):
    lines = [f"各位好，今天我們談「{topic}」。"]
    lines += [f"多數{aud}會遇到："]
    for i, p in enumerate(pts[:3] if pts else ["資訊分散難比較", "稅務流動性不足", "家族對話卡關"], 1):
        lines += [f"{i}. {p}"]
    if use_quote:
        q = pick_brand_quote(cfg); 
        if q: lines += ["", f"我很喜歡的一句話：{q}"]
    lines += ["今天我們用案例與工具，帶大家看一條可複製的路。"]
    return "\n".join(lines)

# -----------------------------
# 產出流程
# -----------------------------
if submitted:
    pts = bullets(key_points)

    # 模板套用
    if preset != "自訂輸入":
        topic, pts, cta = apply_preset(preset, topic, pts, cta)

    if channel == "Facebook 貼文":
        out = gen_fb(audience, topic, pts, cta, brand, CFG, use_quote, use_hashtags)
    elif channel == "LINE 私訊":
        out = gen_line(audience, topic, pts, cta, CFG, use_quote)
    else:
        out = gen_opening(audience, topic, pts, CFG, use_quote)

    # 依口吻調校
    out = style_persona(out, persona, with_emoji)
    # 字數控制
    out = limit_length(out, max_len)

    st.markdown("### ✍️ 產出結果")
    st.code(out, language="markdown")
    st.download_button("下載為 .txt", data=out, file_name=f"mkPRO_{date.today()}.txt")

st.markdown("---")
st.caption("提示：只要修改根目錄 brand.json，即可更新金句、Hashtag 與預設品牌簽名。")
