# legacy_tools/modules/tax_calculator.py
"""
遺產稅計算模組
- 採用相對匯入（.tax_constants）
- 提供相容別名 EstateTaxCalculator，讓舊頁面可直接使用
"""

from .tax_constants import TaxConstants


class TaxCalculator:
    """遺產稅計算工具"""

    @staticmethod
    def calculate_inheritance_tax(total_assets, debts, exemptions):
        """
        計算遺產稅應納稅額
        total_assets: 總資產金額 (float or int)
        debts: 債務金額 (float or int)
        exemptions: 免稅額 (float or int)
        """
        try:
            taxable_amount = float(total_assets) - float(debts) - float(exemptions)
        except Exception:
            # 若輸入不可轉數字，視為 0，避免前端崩潰
            taxable_amount = 0.0

        if taxable_amount <= 0:
            return 0.0

        # 依稅率級距逐段計算
        tax_due = 0.0
        for lower, upper, rate in TaxConstants.INHERITANCE_TAX_BRACKETS:
            if taxable_amount > lower:
                amount_in_bracket = min(taxable_amount, upper) - lower
                if amount_in_bracket > 0:
                    tax_due += amount_in_bracket * rate
            else:
                break

        return round(tax_due, 2)


# ---- 相容別名：舊程式若 import EstateTaxCalculator 也能運作 ----
class EstateTaxCalculator(TaxCalculator):
    """Backward-compatible alias of TaxCalculator"""
    pass
