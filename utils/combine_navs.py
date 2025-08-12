import pandas as pd
from core.currency_converter import CurrencyConverter
from config.config import ASSET_NAV_DATA_PATH

def build_composite_nav(portfolio: dict[str, float]) -> pd.DataFrame:
    """
    Builds a composite NAV time series by weighting each asset's NAV over time.

    Args:
        portfolio (dict): Dictionary mapping asset name to weight (float).

    Returns:
        pd.DataFrame: DataFrame with ['Date', 'NAV_INR'] for the composite portfolio.
    """
    composite_df = None
    curr_conv = CurrencyConverter()

    for name, weight in portfolio.items():
        path = ASSET_NAV_DATA_PATH.get(name)
        if not path:
            raise ValueError(f"Missing path for asset: {name}")
        
        df = pd.read_feather(path)
        df = curr_conv.convert_to_inr(nav_data=df)
        
        df = df[['Date', 'NAV_INR']].copy()
        df['NAV_INR'] *= weight

        if composite_df is None:
            composite_df = df
        else:
            composite_df = composite_df.merge(df, on='Date', how='inner', suffixes=('', f'_{name}'))
            composite_df['NAV_INR'] += composite_df.pop(f'NAV_INR_{name}')

    return composite_df.reset_index(drop=True)
