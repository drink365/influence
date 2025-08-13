# --- modules/insurance_logic.py ---

# 根據輸入條件回傳推薦策略組合

def get_recommendations(age, gender, budget, pay_years, selected_goals):
    # 預設策略結構
    STRATEGIES = [
        {
            "id": "S01",
            "name": "穩健傳承型",
            "match_goals": ["資產傳承", "稅源預備"],
            "description": "以終身壽險為核心，搭配信託架構，專注資產安全移轉與稅源準備。適合資產已累積但尚未規劃移轉工具的客戶。"
        },
        {
            "id": "S02",
            "name": "現金流領回型",
            "match_goals": ["退休現金流", "重大醫療/長照"],
            "description": "以年金與回領型保單為主，強調現金流可預測與彈性調配。適合即將退休或希望建立生活保障者。"
        },
        {
            "id": "S03",
            "name": "多元資產保全型",
            "match_goals": ["資產保全與信託", "子女教育金"],
            "description": "以外幣壽險、教育金規劃、配套信託為主，建立跨代管理與受益條款控制機制。"
        },
        {
            "id": "S04",
            "name": "混合彈性型",
            "match_goals": ["資產傳承", "退休現金流", "稅源預備"],
            "description": "兼顧傳承與領回靈活性，採用混合式保單與定期規劃檢視設計，建立彈性資產結構。"
        },
    ]

    matched = []
    for s in STRATEGIES:
        overlap = list(set(s["match_goals"]) & set(selected_goals))
        if overlap:
            matched.append({
                "id": s["id"],
                "name": s["name"],
                "matched_goals": overlap,
                "description": s["description"]
            })

    return matched[:3]  # 最多顯示 3 策略建議
