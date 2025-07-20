from typing import Literal

from models.UserData import UserData
from config.config import (
    ANNUAL_INFLATION_RATE,
    PRE_RETIREMENT_RETURN_RATE,
    POST_RETIREMENT_RETURN_RATE,
    AVG_LIFE_EXPECTANCY
)

"""
    SWP Calculator: Solves for 
    1) Solve for total and monthly retirement investment required for certain post-retirement monthly withdrawal
    2) Solve for post-retirement monthly withdrawal given investments
    3) Assumes two cases: 1) Aggressive (corpus ~0), 2) Conservative (20% corpus remains)
    4) Solve for how long can the corpus last with a fixed monthly withdrawal
"""

class SWPCalculator:
    def __init__(self):
        self.user_data: UserData = None

    # def run_swp_calculator(
    #     self, 
    #     user_data: UserData,
    #     pre_retirement_return_rate: float = PRE_RETIREMENT_RETURN_RATE,
    #     post_retirement_return_rate: float = POST_RETIREMENT_RETURN_RATE,
    #     annual_inflation_rate: float = ANNUAL_INFLATION_RATE,
    #     avg_life_expectancy: int = AVG_LIFE_EXPECTANCY,
    #     mode: Literal['aggressive', 'conservative'] = 'aggressive'
    # ) -> dict:
    #     self.user_data = user_data
        
    #     future_val = self._compute_retirement_corpus_future_value(
    #         user_data.retirement_savings_amt,
    #         user_data.retirement_sip_amt,
    #         pre_retirement_return_rate,
    #         annual_inflation_rate,
    #         user_data.current_age,
    #         user_data.expected_retirement_age                
    #     )
    
    #     target_corpus = self._compute_target_retirement_corpus(
    #         user_data,
    #         post_retirement_return_rate,
    #         annual_inflation_rate,
    #         avg_life_expectancy
    #     )

    #     if mode == 'conservative':
    #         target_reserve = 0.2 * target_corpus
    #         future_reserve = 0.2 * future_val
    #         target_corpus -= target_reserve
    #         future_val -= future_reserve
    #         future_reserve_val = self._compute_retirement_corpus_future_value(
    #             future_reserve,
    #             0,
    #             pre_retirement_return_rate,
    #             annual_inflation_rate,
    #             user_data.expected_retirement_age,
    #             avg_life_expectancy,
    #         )

    #         target_reserve_val = self._compute_retirement_corpus_future_value(
    #             target_reserve,
    #             0,
    #             pre_retirement_return_rate,
    #             annual_inflation_rate,
    #             user_data.expected_retirement_age,
    #             avg_life_expectancy
    #         )
    
    #     extra_sip_req = self._compute_required_sip_amt(
    #         user_data, 
    #         future_val, 
    #         target_corpus,
    #         pre_retirement_return_rate,
    #         annual_inflation_rate
    #     )
        
    #     current_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, future_val)
       
    #     target_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, target_corpus)

    #     current_monthly_swp = self._compute_monthly_swp_amt(user_data, future_val, post_retirement_return_rate, avg_life_expectancy)
      
    #     # target_monthly_swp = self._compute_monthly_swp_amt(user_data, target_corpus, post_retirement_return_rate, avg_life_expectancy)
    #     target_monthly_swp = self._compute_monthly_swp_amt_with_annual_inflation(user_data, target_corpus, post_retirement_return_rate, avg_life_expectancy, annual_inflation_rate)

    #     schedule = self.month_end_corpus_schedule_with_annual_inflation(user_data, target_corpus, target_monthly_swp, post_retirement_return_rate, avg_life_expectancy, annual_inflation_rate)
    #     with open("corpus_schedule.txt", "w") as f:
    #         for month, balance in schedule:
    #             f.write(f"Month {month:3d}: ₹{balance:,.2f}\n")

    #     # print(schedule)
        
    #     return {
    #         'current_corpus_future_value': future_val,
    #         'ideal_target_corpus': target_corpus,
    #         'extra_sip_required': extra_sip_req,
    #         'manual_swp_current': current_manual_swp,
    #         'manual_swp_target': target_manual_swp,
    #         'safe_swp_current': current_monthly_swp,
    #         'safe_swp_target': target_monthly_swp
    #     }

    def run_swp_calculator(
        self, 
        user_data: UserData,
        pre_retirement_return_rate: float = PRE_RETIREMENT_RETURN_RATE,
        post_retirement_return_rate: float = POST_RETIREMENT_RETURN_RATE,
        annual_inflation_rate: float = ANNUAL_INFLATION_RATE,
        avg_life_expectancy: int = AVG_LIFE_EXPECTANCY,
        mode: Literal['aggressive', 'conservative'] = 'aggressive'
    ) -> dict:
        if mode =='aggressive':
            return self._run_aggressive_calculator(
                user_data,
                pre_retirement_return_rate,
                post_retirement_return_rate,
                avg_life_expectancy,
                annual_inflation_rate,
            )
        elif mode =='conservative':
            return self._run_conservative_calculator(
                user_data,
                pre_retirement_return_rate,
                post_retirement_return_rate,
                avg_life_expectancy,
                annual_inflation_rate,
            )

    def _run_conservative_calculator(
        self,
        user_data: UserData,
        pre_retirement_return_rate: float,
        post_retirement_return_rate: float,
        avg_life_expectancy: int,
        annual_inflation_rate: float,
        reserve_threshold: float = 0.2
    ):
        print('Running conservative analysis.')
        current_age: int = user_data.current_age
        retirement_age: int = user_data.expected_retirement_age
        expected_monthly_expense: float = user_data.expected_retirement_expenses
        retirement_corpus: float = user_data.current_retirement_corpus
        retirement_sip: float = user_data.retirement_sip
        current_reserve_corpus: float = int(retirement_corpus * reserve_threshold)
        # retirement_corpus: float = corpus - current_reserve_corpus
        
        # __________ Current corpus ____________

        current_corpus_future_val = self._compute_retirement_corpus_future_value(
            retirement_corpus,
            retirement_sip,
            pre_retirement_return_rate,
            annual_inflation_rate,
            current_age,
            retirement_age
        )

        # current_monthly_swp = self._compute_monthly_swp_with_annual_inflation(
        #     current_corpus_future_val,
        #     retirement_age,
        #     post_retirement_return_rate,
        #     avg_life_expectancy,
        #     annual_inflation_rate
        # )

        current_monthly_swp = self.compute_swp_with_reserve_pct(
            current_corpus_future_val,
            post_retirement_return_rate,
            avg_life_expectancy - retirement_age,
            reserve_threshold
        )

        # current_monthly_swp = self.compute_swp_with_reserve_and_inflation(
        #     current_corpus_future_val,
        #     post_retirement_return_rate,
        #     annual_inflation_rate,
        #     avg_life_expectancy - retirement_age,
        #     reserve_threshold
        # )

        current_swp_schedule = self._monthly_corpus_schedule_with_reserve(
            current_corpus_future_val,
            current_reserve_corpus,
            current_monthly_swp,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
            annual_inflation_rate
        )

        # __________ Target Corpus ____________

        target_corpus = self._compute_target_retirement_corpus(
            expected_monthly_expense,
            current_age,
            retirement_age,
            post_retirement_return_rate,
            annual_inflation_rate,
            avg_life_expectancy
        )

        target_reserve_corpus = int(target_corpus * reserve_threshold)

        # target_monthly_swp = self._compute_monthly_swp_with_annual_inflation(
        #     target_corpus,
        #     retirement_age,
        #     post_retirement_return_rate,
        #     avg_life_expectancy,
        #     annual_inflation_rate
        # )

        target_monthly_swp = self.compute_swp_with_reserve_pct(
            target_corpus,
            post_retirement_return_rate,
            avg_life_expectancy - retirement_age,
            reserve_threshold
        )

        # target_monthly_swp = self.compute_swp_with_reserve_and_inflation(
        #     target_corpus,
        #     post_retirement_return_rate,
        #     annual_inflation_rate,
        #     avg_life_expectancy - retirement_age,
        #     reserve_threshold
        # )

        target_swp_schedule = self._monthly_corpus_schedule_with_reserve(
            target_corpus,
            target_reserve_corpus,
            target_monthly_swp,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
            annual_inflation_rate
        )

        target_sip = retirement_sip + self._compute_extra_sip_amt(
            current_corpus_future_val,
            target_corpus,
            current_age,
            retirement_age,
            pre_retirement_return_rate,
            annual_inflation_rate
        )

        current_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, current_corpus_future_val)
        target_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, target_corpus)

        corpus_gap = self._compute_corpus_gap(current_corpus_future_val, target_corpus)
        adequacy = self._compute_adequacy(current_corpus_future_val, target_corpus)

        with open('temp/current_schedule.txt', 'w') as f:
            for month, balance, reserve in current_swp_schedule:
                f.write(f"Month {month:3d}: {balance:,.2f} : {reserve:,.2f}\n")

        with open('temp/target_schedule.txt', 'w') as f:
            for month, balance, reserve in target_swp_schedule:
                f.write(f"Month {month:3d}: {balance:,.2f} : {reserve:,.2f}\n")

        return {
            'current_corpus_future_value': current_corpus_future_val,
            'ideal_target_corpus': target_corpus,
            'corpus_gap': corpus_gap,
            'adequacy': adequacy,
            'extra_sip_required': target_sip,
            'manual_swp_current': current_manual_swp,
            'manual_swp_target': target_manual_swp,
            'safe_swp_current': current_monthly_swp,
            'safe_swp_target': target_monthly_swp
        }

        

    def _run_aggressive_calculator(
        self,
        user_data: UserData,
        pre_retirement_return_rate: float,
        post_retirement_return_rate: float,
        avg_life_expectancy: int,
        annual_inflation_rate: float,
    ):
        current_age: int = user_data.current_age
        retirement_age: int = user_data.expected_retirement_age
        expected_monthly_expense: float = user_data.expected_retirement_expenses
        corpus: float = user_data.current_retirement_corpus
        retirement_sip: float = user_data.retirement_sip
        current_reserve_corpus: float = 0
        retirement_corpus: float = corpus - current_reserve_corpus
        
        # __________ Current corpus ____________

        current_corpus_future_val = self._compute_retirement_corpus_future_value(
            retirement_corpus,
            retirement_sip,
            pre_retirement_return_rate,
            annual_inflation_rate,
            current_age,
            retirement_age
        )

        current_monthly_swp = self._compute_monthly_swp_with_annual_inflation(
            current_corpus_future_val,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
            annual_inflation_rate
        )

        current_swp_schedule = self._monthly_corpus_schedule_with_reserve(
            current_corpus_future_val,
            current_reserve_corpus,
            current_monthly_swp,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
            annual_inflation_rate
        )

        # __________ Target Corpus ____________

        target_corpus = self._compute_target_retirement_corpus(
            expected_monthly_expense,
            current_age,
            retirement_age,
            post_retirement_return_rate,
            annual_inflation_rate,
            avg_life_expectancy
        )

        target_reserve_corpus = 0

        target_monthly_swp = self._compute_monthly_swp_amt(
            target_corpus,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
        )

        target_swp_schedule = self._monthly_corpus_schedule_with_reserve(
            target_corpus,
            target_reserve_corpus,
            target_monthly_swp,
            retirement_age,
            post_retirement_return_rate,
            avg_life_expectancy,
            annual_inflation_rate
        )

        target_sip = retirement_sip + self._compute_extra_sip_amt(
            current_corpus_future_val,
            target_corpus,
            current_age,
            retirement_age,
            pre_retirement_return_rate,
            annual_inflation_rate
        )


        current_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, current_corpus_future_val)
        target_manual_swp = self._compute_manual_uninvested_withdrawals(user_data, target_corpus)

        corpus_gap = self._compute_corpus_gap(current_corpus_future_val, target_corpus)
        adequacy = self._compute_adequacy(current_corpus_future_val, target_corpus)

        with open('temp/current_schedule.txt', 'w') as f:
            for month, balance, reserve in current_swp_schedule:
                f.write(f"Month {month:3d}: {balance:,.2f} : {reserve:,.2f}\n")

        with open('temp/target_schedule.txt', 'w') as f:
            for month, balance, reserve in target_swp_schedule:
                f.write(f"Month {month:3d}: {balance:,.2f} : {reserve:,.2f}\n")

        return {
            'current_corpus_future_value': current_corpus_future_val,
            'ideal_target_corpus': target_corpus,
            'corpus_gap': corpus_gap,
            'adequacy': adequacy,
            'extra_sip_required': target_sip,
            'manual_swp_current': current_manual_swp,
            'manual_swp_target': target_manual_swp,
            'safe_swp_current': current_monthly_swp,
            'safe_swp_target': target_monthly_swp
        }

    # def compute_swp_with_reserve_and_inflation(
    #     self,
    #     initial_corpus: float,
    #     post_retirement_return_rate: float,
    #     annual_inflation_rate: float,
    #     withdrawal_years: int,
    #     reserve_pct: float
    # ) -> float:
       
    #     # 1) basic parameters
    #     T = withdrawal_years
    #     n = T * 12
    #     # true monthly compounding return
    #     r_m = (1 + post_retirement_return_rate) ** (1/12) - 1
    #     g   = annual_inflation_rate

    #     # 2) target reserve at end (inflated)
    #     reserve_target = initial_corpus * reserve_pct * (1 + g) ** T
    #     # PV of that reserve back to SWP start
    #     pv_reserve = reserve_target / (1 + r_m) ** n

    #     # 3) corpus available for spending (PV)
    #     pv_for_swp = initial_corpus - pv_reserve
    #     if pv_for_swp <= 0:
    #         raise ValueError("Reserve requirement too large for given corpus/horizon.")

    #     # 4) growing‐annuity present‐value factor, broken into:
    #     #    A = PV factor for 12 constant monthly payments
    #     A = (1 - (1 + r_m) ** -12) / r_m
    #     #    q = annual step‐up ratio discounted back 12 months
    #     q = (1 + g) / (1 + r_m) ** 12
    #     #    geometric series factor over T years
    #     series_factor = (1 - q ** T) / (1 - q)

    #     # PV of a monthly‐for‐12‐months annuity, grown each year by g:
    #     pv_factor = A * series_factor

    #     # 5) solve for W0
    #     W0 = pv_for_swp / pv_factor
    #     return round(W0, 2)


    def compute_swp_with_reserve_pct(
        self,
        initial_corpus: float,
        post_retirement_return_rate: float,
        withdrawal_years: int,
        reserve_pct: float
    ) -> float:
        """
        Compute the flat monthly SWP such that after `withdrawal_years`,
        you still have `reserve_pct` of your initial corpus (inflated by g)
        remaining.

        Args:
            initial_corpus: Corpus at start of SWP (C0).
            post_retirement_return_rate: Effective annual return (e.g. 0.08).
            annual_inflation_rate: Inflation rate for reserve (e.g. 0.05).
            withdrawal_years: Number of years T.
            reserve_pct: Fraction of C0 to leave untouched (e.g. 0.2).

        Returns:
            float: Monthly SWP.
        """
        # Months and true monthly return
        T = withdrawal_years
        n = T * 12
        r_m = (1 + post_retirement_return_rate) ** (1/12) - 1

        # 1) Reserve target at end (inflated)
        reserve_target = initial_corpus * reserve_pct

        # 2) PV of that reserve at retirement
        pv_reserve = reserve_target / (1 + r_m) ** n

        # 3) PV available for SWP
        pv_for_swp = initial_corpus - pv_reserve
        if pv_for_swp <= 0:
            raise ValueError("Reserve requirement too large for given corpus/horizon.")

        # 4) Standard annuity formula on pv_for_swp
        swp = pv_for_swp * r_m / (1 - (1 + r_m) ** -n)
        return round(swp, 2)
    

    # OWN CODE DO NOT DELETE
    def _compute_monthly_swp_amt(
        self, 
        retirement_corpus: float,
        retirement_age: int,
        post_retirement_return_rate: float,
        avg_life_expectancy: int,
    ) -> float:
        # Effective annual rate
        r_eff = post_retirement_return_rate

        # Number of years of withdrawal
        T_years = avg_life_expectancy - retirement_age
        if T_years <= 0:
            raise ValueError('Retirement years is zero or negative.')

        # Convert to true monthly rate via compounding
        r_monthly = (1 + r_eff) ** (1/12) - 1
        n_months = T_years * 12

        # Standard fixed-withdrawal annuity formula
        numerator = retirement_corpus * r_monthly
        denominator = 1 - (1 + r_monthly) ** (-n_months)

        monthly_swp = numerator / denominator
        return round(monthly_swp, 2)
    
    def _compute_corpus_gap(self, current_corpus: float, target_corpus: float):
        return round(target_corpus - current_corpus)

    def _compute_adequacy(self, current_corpus: float, target_corpus: float):
        return round(current_corpus / target_corpus * 100)

    def _compute_monthly_swp_with_annual_inflation(
        self,
        corpus: float,
        retirement_age: int,
        post_retirement_return_rate: float,   # e.g. 0.0978
        avg_life_expectancy: float,
        annual_inflation_rate: float,         # e.g. 0.05
    ) -> float:
        
        years = avg_life_expectancy - retirement_age
        r = (1 + post_retirement_return_rate) ** (1 / 12) - 1  # monthly return
        g = annual_inflation_rate                              # annual increase in SWP
        T = years

        A = (1 - (1 + r) ** -12) / r
        q = (1 + g) / (1 + r) ** 12

        factor = A * (1 - q ** T) / (1 - q)

        W0 = corpus / factor
        return round(W0, 2)


    def _year_end_corpus_schedule(
        self,
        initial_corpus: float,
        monthly_swp: float,
        retirement_age: int,
        post_retirement_return_rate: float,
        avg_life_expectancy: int
    ) -> list[tuple[int, float]]:
        
        withdrawal_years = avg_life_expectancy - retirement_age
        
        # 1) Monthly compounding rate
        r_eff = post_retirement_return_rate
        r_m   = (1 + r_eff) ** (1 / 12) - 1
        n_m   = withdrawal_years * 12

        # 2) Compute SWP if not passed (optional fallback)
        if monthly_swp is None:
            numerator   = initial_corpus * r_m
            denominator = 1 - (1 + r_m) ** (-n_m)
            monthly_swp = numerator / denominator

        # 3) Simulate month-by-month, record at year-end
        bal = initial_corpus
        schedule: list[tuple[int, float]] = [(0, round(bal, 2))]  # Year 0

        for m in range(1, n_m + 1):
            bal = bal * (1 + r_m) - monthly_swp
            if m % 12 == 0:
                year = m // 12
                schedule.append((year, round(bal, 2)))

        return schedule


    def _monthly_corpus_schedule_with_reserve(
        self,
        initial_corpus: float,
        reserve_corpus: float,
        monthly_swp: float,
        retirement_age: int,
        post_retirement_return_rate: float,
        avg_life_expectancy: int,
        annual_inflation_rate: float
    ) -> list[tuple[int, float, float]]:

        # Total withdrawal horizon
        withdrawal_years = avg_life_expectancy - retirement_age
        total_m = withdrawal_years * 12

        # True monthly return rate
        r_m = (1 + post_retirement_return_rate) ** (1/12) - 1

        # If SWP not provided, compute flat annuity SWP on initial_corpus
        if monthly_swp is None:
            num = initial_corpus * r_m
            den = 1 - (1 + r_m) ** (-total_m)
            monthly_swp = num / den

        core_bal    = initial_corpus
        reserve_bal = reserve_corpus
        current_swp = monthly_swp

        schedule: list[tuple[int, float, float]] = [
            (0, round(core_bal, 2), round(reserve_bal, 2))
        ]

        for m in range(1, total_m + 1):
            # 1) grow both by the monthly return
            core_bal    *= (1 + r_m)
            reserve_bal *= (1 + r_m)

            # 2) withdraw SWP from core only
            core_bal    -= current_swp

            # 3) record month-end
            schedule.append((m, round(core_bal, 2), round(reserve_bal, 2)))

            # 4) at each year-end, inflate SWP and the reserve corpus
            if m % 12 == 0:
                current_swp   *= (1 + annual_inflation_rate)
                reserve_bal   *= (1 + annual_inflation_rate)

        return schedule
    

    def _month_end_corpus_schedule(
        self,
        initial_corpus: float,
        monthly_swp: float,
        retirement_age: int,
        post_retirement_return_rate: float,
        avg_life_expectancy: int
    ) -> list[tuple[int, float]]:
    
        withdrawal_years = avg_life_expectancy - retirement_age

        # 1) derive monthly rate & total months
        r_eff   = post_retirement_return_rate
        r_month = (1 + r_eff) ** (1/12) - 1
        total_m = withdrawal_years * 12

        # 2) compute monthly_swp via closed-form if not provided
        if monthly_swp is None:
            num = initial_corpus * r_month
            den = 1 - (1 + r_month) ** (-total_m)
            monthly_swp = num / den

        # 3) simulate month by month
        bal = initial_corpus
        schedule: list[tuple[int, float]] = []
        schedule.append((0, round(initial_corpus, 2)))
        for m in range(1, total_m + 1):
            # compound first, then withdraw at end of month
            bal = bal * (1 + r_month) - monthly_swp
            schedule.append((m, round(bal, 2)))

        return schedule


    def _year_end_corpus_schedule_with_annual_inflation(
        self,
        initial_corpus: float,
        initial_swp_amount: float,
        retirement_age: float,
        post_retirement_return_rate: float,
        avg_life_expectancy: int,
        annual_inflation_rate: float
    ) -> list[tuple[int, float]]:
        """
        Simulates year-end corpus values for a retirement corpus,
        where monthly SWP increases annually by the inflation rate,
        but remains constant within each year.
        """
        withdrawal_years = avg_life_expectancy - retirement_age
        r_m = (1 + post_retirement_return_rate) ** (1 / 12) - 1
        n_m = withdrawal_years * 12

        bal = initial_corpus
        schedule: list[tuple[int, float]] = [(0, round(bal, 2))]

        current_monthly_swp = initial_swp_amount

        for m in range(1, n_m + 1):
            # compound corpus, then withdraw fixed monthly amount for this year
            bal = bal * (1 + r_m) - current_monthly_swp

            # If end of year, record and increase SWP
            if m % 12 == 0:
                year = m // 12
                schedule.append((year, round(bal, 2)))
                current_monthly_swp *= (1 + annual_inflation_rate)

        return schedule


    def _compute_manual_uninvested_withdrawals(
        self, 
        user_data: UserData, 
        retirement_corpus: float
    ) -> float:
        T = AVG_LIFE_EXPECTANCY - user_data.expected_retirement_age + 1
        if T <= 0:
            raise ValueError('Retirement years is zero.')
        return round(retirement_corpus / (12 * T))


    def _compute_extra_sip_amt(
        self, 
        future_val: float, 
        target_corpus: float,
        current_age: int,
        retirement_age: int,
        pre_retirement_return_rate: float,
        annual_inflation_rate: float
    ) -> float:
        
        # raise NotImplementedError()
        
        # if future_val is None:
        #     future_val = self._compute_retirement_corpus_future_value(user_data)
        # if target_corpus is None:
        #     target_corpus = self._compute_target_retirement_corpus(user_data)


        gap_amt = target_corpus - future_val
        if gap_amt <= 0:
            raise ValueError('[ERROR] Current Retirement Funding is Adequate.')
        
        
        r_g = pre_retirement_return_rate
        T = retirement_age - current_age

        if T <= 0:
            raise ValueError('User already in retirement age.')

        R = (1 + r_g / 12)

        if R < 1:
            raise ValueError('Return rate too low.')

        a = (gap_amt) / (R ** (12 * T) - 1)
        extra_sip_req = (a * r_g) / (12 * R)

        if extra_sip_req <= 0:
            raise ValueError('No SIP required.')
        
        return round(extra_sip_req, 2)


    def _compute_retirement_corpus_future_value(
        self, 
        corpus: float,
        sip_amount: float,
        pre_retirement_return_rate: float,
        annual_inflation_rate: float,
        start_age: int,
        end_age: int
    ) -> float:

        L = corpus
        r_g = pre_retirement_return_rate
        r_i = annual_inflation_rate
        sip = sip_amount
        T = end_age - start_age

        try:
            lumpsum_future = (L * (1 + r_g) ** T) 
            sip_future = (sip * (1 + r_g / 12) * ((1 + r_g / 12) ** (12 * T) - 1) * 12 / r_g)
            final_value = (lumpsum_future + sip_future) * (1 + r_i) ** T
            return round(final_value)
        except ZeroDivisionError:
            # raise InvalidFinanceParameterError("err", "err")
            pass


    def _compute_target_retirement_corpus(
        self, 
        expected_monthly_expense: float,
        current_age: int,
        retirement_age: int,
        post_retirement_return_rate: float,
        annual_inflation_rate: float,
        avg_life_expectancy: int
    ) -> float:

        # curr_age = self.user_data.current_age
        # retirement_age = self.user_data.expected_retirement_age
        exp_future_expenses = expected_monthly_expense
        inflation = annual_inflation_rate
        time_to_retirement = retirement_age - current_age
        time_post_retirement = avg_life_expectancy - retirement_age


        # Input validation
        if time_to_retirement <= 0:
            raise ValueError("Retirement age must be greater than present age.")
        if time_post_retirement <= 0:
            raise ValueError("Life expectancy must be greater than retirement age.")

        # Calculate future expenses at retirement (adjusted for inflation)
        years_to_retirement = time_to_retirement
        future_expenses = exp_future_expenses * (1 + inflation) ** years_to_retirement

        # Calculate real rate of return (adjusting post-retirement returns for inflation)
        real_return = ((1 + post_retirement_return_rate) / (1 + inflation)) - 1

        # Calculate required retirement corpus (PV of annuity due)
        retirement_years = time_post_retirement
        if abs(real_return) < 1e-6:  # Handle near-zero real return
            target_corpus = future_expenses * retirement_years * 12  # Monthly payouts
        else:
            target_corpus = future_expenses * (1 - (1 + real_return / 12) ** (-retirement_years * 12)) / (real_return / 12)

        return round(target_corpus)

    ## DO NOT DELETE
    # def _month_end_corpus_schedule(
    #     self,
    #     initial_corpus: float,
    #     reserve_corpus: float,
    #     monthly_swp: float,
    #     retirement_age: int,
    #     post_retirement_return_rate: float,
    #     avg_life_expectancy: int,
    #     annual_inflation_rate: float
    # ) -> list[tuple[int, float]]:
        
    #     withdrawal_years = avg_life_expectancy - retirement_age

    #     # 1) derive monthly rate & total months
    #     r_eff   = post_retirement_return_rate
    #     r_month = (1 + r_eff) ** (1 / 12) - 1
    #     total_m = withdrawal_years * 12

    #     # 2) compute monthly_swp via closed-form if not provided
    #     if monthly_swp is None:
    #         num = initial_corpus * r_month
    #         den = 1 - (1 + r_month) ** (-total_m)
    #         monthly_swp = num / den

    #     # 3) simulate month by month with yearly SWP increase
    #     bal = initial_corpus
    #     current_swp = monthly_swp
    #     schedule: list[tuple[int, float]] = [(0, round(bal, 2))]

    #     for m in range(1, total_m + 1):
    #         bal = bal * (1 + r_month) - current_swp
    #         schedule.append((m, round(bal, 2)))

    #         # increase SWP after every 12 months (end of year)
    #         if m % 12 == 0:
    #             current_swp *= (1 + annual_inflation_rate)

    #     return schedule