# pages/Booking.py
# 預約：日期選擇 + 時段下拉（上午/下午/不限） + 必填驗證(≥5字) + SMTP 通知 + BookingRepo/EventRepo
# --------------------------------------------------------------------
# st.secrets 設定（與你另一 repo 一致，使用大寫 SMTP）：
# [SMTP]
# HOST = "smtp.gmail.com"
# PORT = 587
# USER = "your_account@gmail.com"
# PASS = "your_app_password"
# FROM = "your_account@gmail.com"
# ADMIN_EMAIL = "123@gracefo.com"
# # 企業郵件如走 465，可把 PORT 改成 465（程式仍用 STARTTLS，若需改 SSL 另告知）
# --------------------------------------------------------------------

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from datetime import datetime, date
from typing import Optional, Tuple, Dict, Any

import streamlit as st

# ==== 頁面設定 ====
st.set_page_config(page_title="預約", page_icon="📅", layout="centered")

# ==== 匯入資料倉庫（若無模組則安全後備）====
USE_REPOS = True
try:
    from src.repos.booking_repo import BookingRepo
    from src.repos.event_repo import EventRepo
except Exception:
    USE_REPOS = False

# ==== 讀取 Session / Query 的 case_id（支援自動帶入）====
prefill = st.session_state.get("incoming_case_id")
q = st.query_params
q_case = q.get("case", "") if isinstance(q.get("case"), str) else (q.get("case")[0] if q.get("case") else "")

# ==== 樣式 ====
st.markdown("""
<style>
  .card {background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;}
  .ok-badge {display:inline-block;background:#059669;color:white;padding:2px 8px;border-radius:999px;font-size:12px;}
  .warn-badge {display:inline-block;background:#b45309;color:white;padding:2px 8px;border-radius:999px;font-size:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <h2 style="margin:0 0 .5rem 0;">📅 預約顧問</h2>
  <p style="margin:0;color:#334155">
    請留下您的聯絡資訊與想諮詢的重點，我們將於一個工作日內與您聯繫。<br>
    ※ 個資僅用於聯繫與提供服務，不另作其他用途。
  </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ==== 表單欄位 ====
case_id = st.text_input("案件碼（可選）", value=prefill or q_case or "")
name = st.text_input("姓名/稱呼 *")
phone = st.text_input("手機 *")
email = st.text_input("Email（可選）")

col_time1, col_time2 = st.columns(2)
with col_time1:
    meet_date: date = st.date_input("偏好日期 *", value=date.today())
with col_time2:
    period = st.selectbox("偏好時段（下拉） *", ["不限", "上午（09:00–12:00）", "下午（13:00–17:00）"], index=0)

focus = st.text_area(
    "想諮詢的重點（必填，至少 5 個字） *",
    height=140,
    placeholder="例：家族股權與遺產稅源預留，想先釐清保單與信託搭配…"
)
note = st.text_area("備註（可選）", height=100, placeholder="可提供方便聯絡時段、特殊需求等")
agree = st.checkbox("我已閱讀並同意隱私權政策與資料使用說明。")

# ==== 驗證 ====
def _invalid_reason() -> Optional[str]:
    if not name.strip():
        return "請填寫姓名/稱呼。"
    if not phone.strip():
        return "請填寫手機。"
    if len(focus.strip()) < 5:
        return "「想諮詢的重點」需至少 5 個字，請再補充一些內容。"
    if not agree:
        return "請勾選同意隱私權政策與資料使用說明。"
    return None

# ==== SMTP 設定（使用大寫 SMTP）====
def _smtp_cfg() -> Tuple[Optional[Dict[str, Any]], Optional[list]]:
    s = st.secrets.get("SMTP", {})
    req = ["HOST", "PORT", "USER", "PASS", "FROM", "ADMIN_EMAIL"]
    miss = [k for k in req if not s.get(k)]
    if miss:
        return None, miss
    return s, None

def send_email(to_email: str, subject: str, body: str) -> bool:
    cfg, miss = _smtp_cfg()
    if miss:
        return False
    try:
        with smtplib.SMTP(cfg["HOST"], int(cfg["PORT"])) as server:
            server.starttls()
            server.login(cfg["USER"], cfg["PASS"])
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = cfg["FROM"]
            msg["To"] = to_email
            msg.set_content(body)
            server.send_message(msg)
        return True
    except Exception:
        return False

# ==== 送出 ====
disabled_btn = (
    (not agree) or
    (not name.strip()) or
    (not phone.strip()) or
    (len(focus.strip()) < 5)
)
if st.button("送出預約", type="primary", disabled=disabled_btn):
    date_str = meet_date.strftime("%Y-%m-%d")
    # timeslot 欄位沿用舊結構（方便後端相容）：日期｜時段｜（備註）
    timeslot_str = f"{date_str}｜{period}"
    if note.strip():
        timeslot_str += f"｜{note.strip()}"

    # 建立資料（優先用你的 Repo；若沒有就後備）
    if USE_REPOS:
        try:
            bid = BookingRepo.create({
                "case_id": case_id or None,
                "name": name.strip(),
                "phone": phone.strip(),
                "email": email.strip() or None,
                "timeslot": timeslot_str,          # 仍存 timeslot，內含 日期 + 時段 (+ 備註)
                "focus": focus.strip(),
                "note": note.strip() or None,
                "meet_date": date_str,             # 若你的表結構支援，也同時存明確欄位
                "meet_period": period,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
        except Exception:
            bid = int(datetime.now().timestamp())  # 後備：時間戳代替
        try:
            EventRepo.log(case_id or "N/A", "BOOKING_CREATED", {
                "booking_id": bid,
                "meet_date": date_str,
                "meet_period": period
            })
        except Exception:
            pass
    else:
        bid = int(datetime.now().timestamp())

    # 畫面回饋
    st.success("預約資訊已送出，顧問將於一個工作日內與您聯繫！")
    st.caption(f"Booking ID：#{bid}")

    # 寄送通知（管理者 + 客戶）
    cfg, miss = _smtp_cfg()
    if cfg:
        admin_body = (
            f"【新預約通知】\n\n"
            f"Booking ID：#{bid}\n"
            f"案件碼：{case_id or 'N/A'}\n"
            f"姓名：{name}\n"
            f"手機：{phone}\n"
            f"Email：{email or '—'}\n"
            f"偏好日期：{date_str}\n"
            f"偏好時段：{period}\n"
            f"重點：\n{focus.strip()}\n\n"
            f"備註：\n{note.strip() or '—'}\n"
            f"提交時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        ok_admin = send_email(cfg["ADMIN_EMAIL"], f"[新預約] #{bid} {name}", admin_body)

        if email.strip():
            client_body = (
                f"{name} 您好：\n\n"
                f"我們已收到您的預約，將於一個工作日內與您聯繫。\n\n"
                f"Booking ID：#{bid}\n"
                f"偏好日期：{date_str}\n"
                f"偏好時段：{period}\n"
                f"您提供的重點：\n{focus.strip()}\n\n"
                f"若需更動預約，歡迎直接回覆此信。"
            )
            ok_client = send_email(email.strip(), "我們已收到您的預約", client_body)
        else:
            ok_client = True  # 沒填 Email 就不寄，不阻擋流程

        # 顯示寄信狀態
        if ok_admin:
            st.markdown('<span class="ok-badge">通知</span> 已寄出管理者通知信', unsafe_allow_html=True)
        else:
            st.markdown('<span class="warn-badge">通知</span> 通知信寄出失敗（請檢查 SMTP 設定）', unsafe_allow_html=True)

        if not ok_client and email.strip():
            st.markdown('<span class="warn-badge">客戶通知</span> 寄給客戶的確認信失敗', unsafe_allow_html=True)
    else:
        st.markdown('<span class="warn-badge">提醒</span> 未設定 SMTP，僅畫面顯示成功，未寄出 Email。', unsafe_allow_html=True)

    # 螢幕備份（避免未設 SMTP 時遺漏）
    with st.expander("查看本次提交內容（可複製備份）", expanded=False):
        st.json({
            "booking_id": bid,
            "case_id": case_id or None,
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip() or None,
            "meet_date": date_str,
            "meet_period": period,
            "timeslot": timeslot_str,
            "focus": focus.strip(),
            "note": note.strip() or None,
        })

    # 清除 session 預填，避免殘留
    st.session_state.pop("incoming_case_id", None)
