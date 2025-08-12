# XIRR_Calculator.py

from __future__ import annotations
import pandas as pd
import pyxirr
from typing import List, Literal
from utils.combine_navs import build_composite_nav
from config.config import ENABLE_XIRR_DUMP


class XirrCalculator:
    def __init__(self):
        pass

    def _compute_rolling_window_xirrs(
        self, df: pd.DataFrame, time_horizon: int, sip_amount: float = 1000
    ) -> List[float]:
        """
        Compute XIRRs for rolling SIP windows using historical data.
        """
        months = time_horizon * 12
        xirrs: List[float] = []

        for start in range(len(df) - months):
            window = df.iloc[start : start + months + 1]
            if len(window) < months + 1:
                continue

            dates = window['Date'].iloc[:months].tolist()
            amounts = [-sip_amount] * months

            start_prices = window['NAV_INR'].iloc[:months].values
            end_price = window['NAV_INR'].iloc[months]

            units = [sip_amount / p for p in start_prices]
            total_units = sum(units)
            maturity_value = total_units * end_price

            dates.append(window['Date'].iloc[months])
            amounts.append(maturity_value)

            try:
                xirr_val = pyxirr.xirr(dict(zip(dates, amounts))) * 100
                xirrs.append(xirr_val)
            except Exception as e:
                raise ValueError(e)
        
        return xirrs

    def compute_asset_rolling_xirr(
        self,
        time_horizon: int,
        df: pd.DataFrame | None = None,
        feather_path: str | None = None,
        mode: Literal["mean", "median", "optimistic", "pessimistic"] = "median"
    ) -> float:
        """
        :param time_horizon: Investment horizon in years.
        :param feather_path: If provided, reads this Feather file into df.
        :param df: If provided, uses this DataFrame directly (skips reading from file).
        :param mode: 'median', 'mean', 'pessimistic', or 'optimistic'.
        :return: Estimated return rate (% CAGR).
        """
        if df is None:
            if feather_path is None:
                raise ValueError()
            df = pd.read_feather(feather_path)

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)

        xirrs = self._compute_rolling_window_xirrs(df, time_horizon)
        if not xirrs:
            print('[WARNING] Inadequate data to compute returns for given time horizon. Defaulting to maximum available data.\n')
            xirrs = self._compute_rolling_window_xirrs(df, int(len(df) / 12 - 1))
            if not xirrs:
                raise ValueError('Not enough data to compute returns.')
        
        series = pd.Series(xirrs)

        if ENABLE_XIRR_DUMP:
            series.to_csv('temp/xirr_dump.csv')
           
        if mode == "median":
            return round(series.median(), 2)
        elif mode == "mean":
            return round(series.mean(), 2)
        elif mode == "pessimistic":
            return round(series.quantile(0.25), 2)
        elif mode == "optimistic":
            return round(series.quantile(0.75), 2)
        else:
            raise ValueError()
        
    def compute_portfolio_rolling_xirr(
        self, 
        portfolio: dict[str, float],
        time_horizon: int,
        mode: Literal["mean", "median", "optimistic", "pessimistic"] = "median"
    ) -> float:
        composite_df = build_composite_nav(portfolio=portfolio)

        if 'NAV_INR' not in composite_df.columns:
            raise ValueError("Input DataFrame must contain 'NAV_INR' column.")

        return self.compute_asset_rolling_xirr(time_horizon=time_horizon, df=composite_df, mode=mode) / 100