# legacy_tools/modules/tax_calculator.py
"""
遺產稅計算模組
改用相對匯入，避免 ModuleNotFoundError
"""

from .tax_constants import TaxConstants

class TaxCalculator:
    """遺產稅計算工具"""

    @staticmethod
    def calculate_inheritance_tax(total_assets, debts, exemptions):
        """
        計算遺產稅應納稅額
        total_assets: 總資產金額
        debts: 債務金額
        exemptions: 免稅額
        """
        taxable_amount = total_assets - debts - exemptions
        if taxable_amount <= 0:
            return 0

        # 使用稅率級距計算
        tax_due = 0
        for bracket in TaxConstants.INHERITANCE_TAX_BRACKETS:
            lower, upper, rate = bracket
            if taxable_amount > lower:
                amount_in_bracket = min(taxable_amount, upper) - lower
                tax_due += amount_in_bracket * rate
            else:
                break
        return round(tax_due, 2)
