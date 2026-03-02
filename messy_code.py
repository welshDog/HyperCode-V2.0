# Constants
MONTHS_IN_YEAR = 12
AFFORDABILITY_THRESHOLD = 0.3

def calculate_monthly_payment(principal, annual_interest_rate, years):
    """
    Calculates the monthly mortgage payment.

    Args:
        principal: The principal loan amount.
        annual_interest_rate: The annual interest rate (as a percentage).
        years: The loan term in years.

    Returns:
        The monthly payment amount.
    """
    if annual_interest_rate == 0:
        return principal / (years * MONTHS_IN_YEAR)

    monthly_interest_rate = annual_interest_rate / 100 / MONTHS_IN_YEAR
    number_of_payments = years * MONTHS_IN_YEAR

    numerator = monthly_interest_rate * ((1 + monthly_interest_rate) ** number_of_payments)
    denominator = ((1 + monthly_interest_rate) ** number_of_payments) - 1
    
    return principal * (numerator / denominator)

def is_affordable(salary, monthly_payment):
    """
    Checks if a monthly payment is affordable based on a salary.

    Args:
        salary: The annual salary.
        monthly_payment: The monthly payment amount.

    Returns:
        True if the payment is affordable, False otherwise.
    """
    return monthly_payment <= (salary / MONTHS_IN_YEAR * AFFORDABILITY_THRESHOLD)

if __name__ == '__main__':
    # Example usage:
    principal_amount = 500000
    interest_rate = 5.0
    loan_term_years = 30
    annual_salary = 120000

    payment = calculate_monthly_payment(principal_amount, interest_rate, loan_term_years)
    print(f"Your monthly payment is: {payment:.2f}")

    if is_affordable(annual_salary, payment):
        print("You can afford it.")
    else:
        print("This may be too expensive for you.")
