# 清理說明

以下頁面已從「精簡版」中移除，避免重複與權限依賴（例如登入、Email、DB Secrets）。
需要時可從舊版 repo 取回。

移除頁：
- 0a_AI_Copilot.py
- 1_Dashboard.py
- 1_Home.py
- 2_Diagnostic.py
- 3_Result.py
- 5_estate_tax.py
- 6_Bookings_Admin.py
- 7_Events_Admin.py
- 7_asset_map.py
- 8_Advisor_Dashboard.py
- 8_insurance_strategy.py
- 9_Credits_Admin.py
- Login.py
- Share.py
- _nav_import.py

保留頁：
- 0_Tools.py
- 0b_AI_Copilot_Pro.py
- Tools_EstateTax.py
- Tools_AssetMap.py
- Tools_InsuranceStrategy.py
- 4_Booking.py

其他：保留 `src/` 與 `legacy_tools/modules/` 以支援工具運作；
PDF 匯出統一由 `legacy_tools/modules/pdf_generator.py` 處理（含 brand.json 與中文字型）。
