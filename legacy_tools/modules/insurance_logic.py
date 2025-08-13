# legacy_tools/modules/insurance_logic.py
from __future__ import annotations

from typing import List, Dict

# 簡單固定匯率；之後要動態匯率再接資料源即可
FX_USD_TWD: float = 32.0

def _frontload_text(pay_years: int) -> str:
    # 依你要求：1 年期不顯示；>1 年顯示「前期視資金狀況加保；」
    return "" if pay_years == 1 else "前期視資金狀況加保；"

def _tier(budget_wan: float, currency: str) -> str:
    twd_wan = budget_wan * (FX_USD_TWD if currency == "USD" else 1.0)
    if twd_wan >= 1000:
        return "高端預算"
    if twd_wan >= 300:
        return "進階預算"
    if twd_wan >= 100:
        return "標準預算"
    return "入門預算"

def recommend_strategies(
    age: int,
    gender: str,
    budget: float,     # 單位：萬 <currency>
    currency: str,     # "TWD" / "USD"
    pay_years: int,
    goals: List[str],
) -> List[Dict]:
    """回傳策略清單：每個元素含 name / why / fit / description。"""
    twd_wan = budget * (FX_USD_TWD if currency == "USD" else 1.0)
    tier = _tier(budget, currency)
    frontload = _frontload_text(pay_years)

    L: List[Dict] = []

    if "傳承" in goals or "稅源" in goals or "企業主" in goals:
        L.append({
            "name": "終身壽險＋增額結構（預留稅源）",
            "fit": ["傳承", "稅源", "企業主"],
            "why": "以壽險作為稅源準備，另兼具資產傳承的確定性與效率。",
            "description": (
                f"{frontload}建議以 {pay_years} 年繳，調整基本保額與增額比例；"
                "保單可作為流動性工具（保單借款），亦可搭配信託或股權設計。"
            ).strip()
        })

    if "退休" in goals or "資產配置" in goals:
        L.append({
            "name": "增額型終身壽＋現金流配置",
            "fit": ["退休", "資產配置"],
            "why": "強化中長期現金值成長，兼顧風險管控與退休現金流。",
            "description": (
                f"{frontload}採 {pay_years} 年期；以定率增額提高長期現金值，"
                "到期後視利率與家庭現金流需求調整保單借款或減額繳清。"
            ).strip()
        })

    if "醫療" in goals or "長照" in goals:
        L.append({
            "name": "醫療險／長照險（保障缺口補強）",
            "fit": ["醫療", "長照"],
            "why": "轉嫁重大醫療與長期照護風險，避免侵蝕家族資產。",
            "description": "優先補齊實支實付與長照給付；與壽險方案協同配置保費。"
        })

    if "教育" in goals:
        L.append({
            "name": "教育金專案（保值與安全性優先）",
            "fit": ["教育"],
            "why": "確保教育基金安全到位，降低市場波動影響。",
            "description": f"{frontload}搭配年期 {pay_years}；屆期以減額或保單借款取得資金。".strip()
        })

    # 預算敏感度提示（僅文字說明，不改策略）
    if twd_wan < 100:
        L.append({
            "name": "入門預算提示",
            "fit": [tier],
            "why": "入門預算應聚焦關鍵保障與稅源準備的最低門檻。",
            "description": "可先以定期壽險＋醫療長照補足缺口，逐步升級到終身壽險結構。"
        })

    return L
