# source/Asset.py

import pandas as pd
import pyxirr

from core.xirr_calculator import XirrCalculator
from core.currency_converter import CurrencyConverter


class Asset:
    """
    Represents a single asset (e.g., smallcap, debt, gold) with:
      - name (e.g. "smallcap")
      - weight (fraction of the total portfolio)
      - path to its historical NAV (feather) file
      - methods to compute expected return, per-asset SIP, and per-asset XIRR
    """

    def __init__(
        self,
        name: str,
        feather_path: str,
        weight: float,
        is_sip_start_of_month: bool = False
    ):
        """
        :param name: Asset name (e.g., "smallcap").
        :param feather_path: Path to that asset's historical price (Feather format).
        :param weight: Fraction of total portfolio allocated to this asset (must sum to 1).
        :param is_sip_start_of_month: If True, SIP is at month-start; otherwise month-end.
        """
        self.name = name
        self.feather_path = feather_path
        self.weight = weight
        self.is_sip_start_of_month = is_sip_start_of_month

        self.expected_return_rate: float = 0.0   # % annual, from rolling‐window XIRR
        self.asset_sip_amount: float = 0.0       # ₹ SIP per month for this asset
        self.asset_xirr: float = 0.0             # XIRR % computed for this asset
        self._df: pd.DataFrame | None = None     # loaded historical DataFrame


    def convert_navs_to_inr(self) -> None:
        """
        Converts the NAV of the historical data to inr using date-matched conversion rates.
        """
        curr_conv = CurrencyConverter()
        if self._df is None:
            self.load_history()

        self._df = curr_conv.convert_to_inr(nav_data=self._df)
            

    def load_history(self) -> None:
        """
        Reads the Feather file into self._df, normalizes dates to midnight, and sorts.
        """
        df = pd.read_feather(self.feather_path)
        df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
        df = df.sort_values('Date').reset_index(drop=True)
        self._df = df

            
    def compute_rolling_xirr(
        self,
        time_horizon: int,
        mode: str = "median"
    ) -> float:
        """
        Uses SIPReturnForecaster to compute rolling-window SIP XIRR (median/mean/etc.)
        on this asset's history. Stores result in self.expected_return_rate.
        """
        if self._df is None:
            self.load_history()

        xirr_calc = XirrCalculator()

        expected = xirr_calc.compute_rolling_xirr(
            time_horizon=time_horizon,
            df=self._df,
            mode=mode
        )
        self.expected_return_rate = expected
        return expected
