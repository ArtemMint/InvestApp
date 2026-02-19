from fastapi import APIRouter
from app.utils.helpers import log_request

router = APIRouter()

@log_request
@router.get("/", status_code=200)
async def calculate_investment_history(
        principal: int = 1000,
        monthly_contribution: int = 750,
        years: int = 25,
        annual_return: float = 0.12,
        contribution_growth: float = 0.03,
        tax_rate: float = 0.18,
        annual_inflation: float = 0.03
):
    """
    Calculate the investment history over a specified number of years, given an initial principal,
    monthly contributions, annual return rate, and contribution growth rate.
    The function returns a list of dictionaries containing the month, total invested amount,
    total balance, and profit for each month.

    :param principal: Initial investment amount
    :param monthly_contribution: Amount contributed monthly
    :param years: Number of years to calculate the investment history for
    :param annual_return: Expected annual return rate (e.g., 0.12 for 12%)
    :param contribution_growth: Annual growth rate for the monthly contribution (e.g., 0.03 for 3%)
    :param tax_rate: Tax rate applied to the profit (e.g., 0.18 for 18%)
    :param annual_inflation: Annual inflation rate used for discounting the net balance (e.g., 0.03 for 3%)
    :return:

    """
    monthly_rate = annual_return / 12
    total_months = years * 12

    current_balance = principal
    total_invested = principal
    current_pmt = monthly_contribution

    # Array to hold the history of investments for each month
    history = []

    for month in range(1, total_months + 1):
        # Percentage of return for the current month
        interest_earned = current_balance * monthly_rate
        current_balance += interest_earned

        # Increment the balance by the monthly contribution
        current_balance += current_pmt
        total_invested += current_pmt

        # Indexing for contribution growth: every 12 months, increase the monthly contribution by the growth rate
        if month % 12 == 0:
            current_pmt *= (1 + contribution_growth)

        # 2. Calculate taxes (as if we were to close the account now)
        gross_profit = current_balance - total_invested
        # Tax is only taken from the profit. If there is no profit (e.g., market dropped), tax is 0
        actual_tax = (gross_profit * tax_rate) if gross_profit > 0 else 0
        net_balance = current_balance - actual_tax

        # 3. Discounting for inflation to get the "Real Value"
        # Use (month / 12) to accurately discount even partial years
        real_value = net_balance / ((1 + annual_inflation) ** (month / 12))

        # Write the current month's data to the history array
        history.append({
            "month": month,
            "label": f"Рік {month // 12}" if month % 12 == 0 else "",
            "invested": round(total_invested, 2),
            "total_balance": round(current_balance, 2),
            "profit": round(current_balance - total_invested, 2),
            "real_value": round(real_value, 2)
        })

    return history