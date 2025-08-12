from typing import Literal
from config.config import (
    AGGRESSIVE_PORTFOLIO, 
    AVG_LIFE_EXPECTANCY, 
    BALANCED_PORTFOLIO, 
    CONSERVATIVE_PORTFOLIO,
    PRE_RETIREMENT_RETURN_RATE,
    POST_RETIREMENT_RETURN_RATE
)
from core.swp_calculator import SWPCalculator
from core.xirr_calculator import XirrCalculator
from core.exceptions import CriticalInternalError
from models.UserData import UserData
from utils.logger import get_logger

logger = get_logger()

def get_relevant_portfolio(risk_level: Literal['conservative', 'aggressive', 'balanced']):
    """
    Retrieve the investment portfolio allocation corresponding to a given risk level.

    Args:
        risk_level (Literal): Risk tolerance category. Accepted values:
                              - 'conservative': Low-risk portfolio
                              - 'balanced': Medium-risk portfolio
                              - 'aggressive': High-risk portfolio

    Returns:
        dict: Asset allocation for the specified risk category.

    Raises:
        ValueError: If the provided risk level is not one of the accepted values.
    """
    if risk_level == 'conservative':
        return CONSERVATIVE_PORTFOLIO
    if risk_level == 'balanced':
        return BALANCED_PORTFOLIO
    if risk_level == 'aggressive':
        return AGGRESSIVE_PORTFOLIO
    raise ValueError()


def runAnalysis(
    user_data: UserData,
    swp_mode: Literal['aggressive', 'conservative'],
    pre_retirement_risk: Literal['conservative', 'aggressive', 'balanced'],
    post_retirement_risk: Literal['conservative', 'aggressive', 'balanced']
):
    """
    Perform a complete pre-retirement and post-retirement portfolio analysis, 
    followed by a Systematic Withdrawal Plan (SWP) calculation.

    This function:
      1. Determines the user's pre-retirement and post-retirement time horizons.
      2. Selects portfolio allocations for both phases based on risk profiles.
      3. Computes expected rolling XIRR (annualized returns) for each phase.
      4. Runs SWP calculations to estimate required investments/withdrawals.

    Args:
        user_data (UserData): User's financial and demographic inputs, 
                              including current age and retirement goals.
        swp_mode (Literal): Withdrawal mode for SWP calculation.
                            - 'aggressive': Larger withdrawals, shorter sustainability.
                            - 'conservative': Smaller withdrawals, longer sustainability.
        pre_retirement_risk (Literal): Risk profile before retirement.
                                       Accepted: 'conservative', 'aggressive', 'balanced'
        post_retirement_risk (Literal): Risk profile after retirement.
                                        Accepted: 'conservative', 'aggressive', 'balanced'

    Returns:
        dict: SWP calculation results, containing:
              - corpus at retirement
              - sustainable withdrawals
              - portfolio performance estimates

    Raises:
        CriticalInternalError: If required portfolio allocations or computations fail.
    """
    # Time horizon calculations
    time_to_retirement = user_data.expected_retirement_age - user_data.current_age
    time_post_retirement = AVG_LIFE_EXPECTANCY - user_data.expected_retirement_age

    # Get pre-retirement portfolio
    try:
        pre_retirement_portfolio = get_relevant_portfolio(pre_retirement_risk)
        logger.info('Pre-retirement portfolio fetched.')
    except ValueError:
        logger.critical('Relevant portfolio for given pre-retirement risk not found. Aborting.')
        raise CriticalInternalError()
    
    # Get post-retirement portfolio
    try:
        post_retirement_portfolio = get_relevant_portfolio(post_retirement_risk)
        logger.info('Post-retirement portfolio fetched.')
    except ValueError:
        logger.critical('Relevant portfolio for post-retirement risk not found. Aborting.')
        raise CriticalInternalError()

    # Compute rolling XIRR for both periods
    xirr_calc = XirrCalculator()
    try:
        pre_retirement_return_rate = xirr_calc.compute_portfolio_rolling_xirr(
            portfolio=pre_retirement_portfolio, 
            time_horizon=time_to_retirement
        )
        logger.info(f'Pre-retirement return rate computed: {pre_retirement_return_rate}.')
    except Exception:
        logger.warning('Pre-retirement return rate computation failed. Defaulting to fallback.')
        pre_retirement_return_rate = PRE_RETIREMENT_RETURN_RATE
    
    try:
        post_retirement_return_rate = xirr_calc.compute_portfolio_rolling_xirr(
            portfolio=post_retirement_portfolio, 
            time_horizon=time_post_retirement
        )
        logger.info(f'Post-retirement return rate computed: {post_retirement_return_rate}')
    except Exception:
        logger.warning('Post-retirement return rate computation failed. Defaulting to fallback.')
        post_retirement_return_rate = POST_RETIREMENT_RETURN_RATE

    # Run SWP calculator
    swp_calc = SWPCalculator()
    try:
        results = swp_calc.run_swp_calculator(
            user_data,
            pre_retirement_return_rate=pre_retirement_return_rate,
            post_retirement_return_rate=post_retirement_return_rate,
            mode=swp_mode
        )
        logger.info('SWP data computation complete.')
    except Exception as e:
        logger.error('SWP data computation failed. Aborting.')
        logger.exception(e)
        raise CriticalInternalError()

    return results
