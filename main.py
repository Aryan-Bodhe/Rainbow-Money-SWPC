import os
import json
from typing import Literal
import pprint
from core.swp_calculator import SWPCalculator
from core.xirr_calculator import XirrCalculator
from models.UserData import UserData
from config.config import (
    AVG_LIFE_EXPECTANCY,
    AGGRESSIVE_PORTFOLIO,
    BALANCED_PORTFOLIO,
    CONSERVATIVE_PORTFOLIO,
)

def print_data(data: dict):
    pprint.pprint(data)

def read_json(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def get_relevant_portfolio(risk_level: Literal['conservative', 'aggressive', 'balanced']):
    if risk_level == 'conservative':
        return CONSERVATIVE_PORTFOLIO
    if risk_level == 'balanced':
        return BALANCED_PORTFOLIO
    if risk_level == 'aggressive':
        return AGGRESSIVE_PORTFOLIO

def display_data(results: dict):
    print(f"Future value of investments : {results['current_corpus_future_value']:,}.")
    print(f"Required Target Corpus      : {results['ideal_target_corpus']:,}.")
    print(f"Corpus Gap                  : {results['corpus_gap']:,}.")
    print(f"Retirement Adequacy         : {results['adequacy']}%.")
    print(f"Extra SIP required          : {results['extra_sip_required']:,}.")
    print(f"Uninvested SWP (current)    : {results['manual_swp_current']:,}.")
    print(f"Uninvested SWP (target)     : {results['manual_swp_target']:,}.")
    print(f"Sustainable SWP (current)   : {results['safe_swp_current']:,}.")
    print(f"Sustainable SWP (target)    : {results['safe_swp_target']:,}.")


def runTest(
    data_path: str,
    pre_retirement_risk: Literal['conservative', 'aggressive', 'balanced'],
    post_retirement_risk: Literal['conservative', 'aggressive', 'balanced']
):
    print('\n------------------------------------------------------------')
    print('Retirement SWP Calculator.\n')
    raw_data = read_json(data_path)
    user_data = UserData(**raw_data)
    time_to_retirement = user_data.expected_retirement_age - user_data.current_age
    time_post_retirement = AVG_LIFE_EXPECTANCY - user_data.expected_retirement_age

    pre_retirement_portfolio = get_relevant_portfolio(pre_retirement_risk)
    post_retirement_portfolio = get_relevant_portfolio(post_retirement_risk)

    xirr_calc = XirrCalculator()
    pre_retirement_return_rate = xirr_calc.compute_portfolio_rolling_xirr(
        portfolio=pre_retirement_portfolio, 
        time_horizon=time_to_retirement
    )
    
    post_retirement_return_rate = xirr_calc.compute_portfolio_rolling_xirr(
        portfolio=post_retirement_portfolio, 
        time_horizon=time_post_retirement
    )

    print(f'Pre-retirement Return Rate  : {pre_retirement_return_rate*100:.2f}.')
    print(f'Post-Retirement Return Rate : {post_retirement_return_rate*100:.2f}.')
    print()

    swp_calc = SWPCalculator()
    
    try:
        results = swp_calc.run_swp_calculator(
            user_data,
            pre_retirement_return_rate=pre_retirement_return_rate,
            post_retirement_return_rate=post_retirement_return_rate,
            mode='conservative'
        )

        display_data(results)
    except Exception as e:
        print()
        print(e)
        print_data(user_data.model_dump())

    print('\n------------------------------------------------------------\n')

def runTesting():
    os.system('clear')
    runTest(
        # data_path='temp/profiles/young.json',
        data_path='temp/profiles/middle.json',
        # data_path='temp/profiles/old.json',
        pre_retirement_risk='aggressive',
        post_retirement_risk='conservative'
    )

if __name__ == '__main__':
    runTesting()


# user_data = UserData(
#     current_age=45,
#     expected_retirement_age=60,
#     current_expenses=100000,
#     expected_retirement_expenses=100000,
#     retirement_savings_amt=2000000,
#     retirement_sip_amt=000
# )

# calc = SWPCalculator()
# calc.run_swp_calculator(user_data)