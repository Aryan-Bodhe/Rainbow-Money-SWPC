import os

ANNUAL_INFLATION_RATE = 0.05
PRE_RETIREMENT_RETURN_RATE = 0.12
POST_RETIREMENT_RETURN_RATE = 0.08
AVG_LIFE_EXPECTANCY = 75

NUM_SIMULATIONS = 10000
TARGET_PROB_OF_SUCCESS = 0.95
ENABLE_XIRR_DUMP = False

LOGGING_DIR = 'logs/'
LOGGING_LIMIT_DAYS = 5

CONSERVATIVE_PORTFOLIO = {
    "largecap": 0.1,
    "debt": 0.55,
    "gold": 0.35
}

BALANCED_PORTFOLIO = {
    "largecap": 0.30,
    "s&p_500": 0.20,
    "gold": 0.5
}

AGGRESSIVE_PORTFOLIO = {
    "largecap": 0.7,
    "s&p_500": 0.1,
    "gold": 0.2
}

FOREX_RATES_DIR = os.path.join(os.getcwd(), 'data/monthly_forex/')
ASSET_NAV_DATA_PATH = {
    "largecap": os.path.join(os.getcwd(), "data/monthly_nav/largecap.feather"),
    "s&p_500":  os.path.join(os.getcwd(), "data/monthly_nav/sp500.feather"),
    "gold":     os.path.join(os.getcwd(), "data/monthly_nav/gold.feather"),
    "debt":     os.path.join(os.getcwd(), "data/monthly_nav/debt.feather")
}

