import math
import decimal
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

# Set decimal precision
decimal.getcontext().prec = 28


def calculate_monthly_payment(principal: Decimal, annual_interest_rate: Decimal, term_years: int) -> Decimal:
    """
    Calculate the monthly payment for a loan using the standard amortization formula.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as a percentage (e.g., 5.5 for 5.5%)
        term_years: The loan term in years
        
    Returns:
        The monthly payment amount
    """
    # Convert annual interest rate to monthly decimal rate
    monthly_rate = annual_interest_rate / Decimal('100') / Decimal('12')
    
    # Calculate number of payments
    num_payments = int(term_years * 12)
    
    # Handle edge case of zero interest rate
    if monthly_rate == 0:
        return principal / Decimal(num_payments)
    
    # Calculate monthly payment using the amortization formula
    x = (1 + monthly_rate) ** num_payments
    monthly_payment = principal * monthly_rate * x / (x - 1)
    
    # Round to 2 decimal places
    return monthly_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)


def calculate_interest_only_payment(principal: Decimal, annual_interest_rate: Decimal) -> Decimal:
    """
    Calculate the monthly payment for an interest-only loan.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as a percentage
        
    Returns:
        The monthly interest-only payment amount
    """
    monthly_rate = annual_interest_rate / Decimal('100') / Decimal('12')
    monthly_payment = principal * monthly_rate
    
    return monthly_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)


def generate_amortization_schedule(
    principal: Decimal, 
    annual_interest_rate: Decimal, 
    term_years: int,
    start_date: date = None
) -> List[Dict]:
    """
    Generate a complete amortization schedule for a loan.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as a percentage
        term_years: The loan term in years
        start_date: The start date for the loan (defaults to today)
        
    Returns:
        A list of dictionaries containing payment details for each period
    """
    if start_date is None:
        start_date = date.today()
    
    monthly_rate = annual_interest_rate / Decimal('100') / Decimal('12')
    num_payments = int(term_years * 12)
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, term_years)
    
    schedule = []
    balance = principal
    payment_date = start_date
    
    for payment_num in range(1, num_payments + 1):
        # Calculate interest for this period
        interest_payment = balance * monthly_rate
        
        # Calculate principal for this period
        principal_payment = monthly_payment - interest_payment
        
        # Update the remaining balance
        balance = balance - principal_payment
        
        # Handle potential rounding issues for the final payment
        if payment_num == num_payments:
            if balance > 0:
                principal_payment += balance
                monthly_payment = principal_payment + interest_payment
            balance = Decimal('0')
        
        # Add a month to the payment date
        payment_date = add_one_month(payment_date)
        
        # Add this payment to the schedule
        schedule.append({
            'payment_number': payment_num,
            'payment_date': payment_date,
            'payment_amount': monthly_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'principal_amount': principal_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'interest_amount': interest_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'remaining_balance': balance.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        })
    
    return schedule


def generate_interest_only_schedule(
    principal: Decimal, 
    annual_interest_rate: Decimal, 
    term_years: int,
    start_date: date = None
) -> List[Dict]:
    """
    Generate a payment schedule for an interest-only loan.
    
    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as a percentage
        term_years: The loan term in years
        start_date: The start date for the loan (defaults to today)
        
    Returns:
        A list of dictionaries containing payment details for each period
    """
    if start_date is None:
        start_date = date.today()
    
    monthly_rate = annual_interest_rate / Decimal('100') / Decimal('12')
    num_payments = int(term_years * 12)
    monthly_payment = calculate_interest_only_payment(principal, annual_interest_rate)
    
    schedule = []
    balance = principal
    payment_date = start_date
    
    for payment_num in range(1, num_payments + 1):
        # For interest-only loans, all payment goes to interest except the last one
        interest_payment = monthly_payment
        principal_payment = Decimal('0')
        
        # For the final payment, add the principal
        if payment_num == num_payments:
            principal_payment = principal
            monthly_payment = principal_payment + interest_payment
            balance = Decimal('0')
        
        # Add a month to the payment date
        payment_date = add_one_month(payment_date)
        
        # Add this payment to the schedule
        schedule.append({
            'payment_number': payment_num,
            'payment_date': payment_date,
            'payment_amount': monthly_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'principal_amount': principal_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'interest_amount': interest_payment.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
            'remaining_balance': balance.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        })
    
    return schedule


def calculate_loan_summary(schedule: List[Dict]) -> Dict:
    """
    Calculate summary statistics for a loan based on its payment schedule.
    
    Args:
        schedule: The amortization schedule as a list of dictionaries
        
    Returns:
        A dictionary containing summary statistics
    """
    total_payments = sum(payment['payment_amount'] for payment in schedule)
    total_interest = sum(payment['interest_amount'] for payment in schedule)
    total_principal = sum(payment['principal_amount'] for payment in schedule)
    
    return {
        'total_payments': total_payments.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
        'total_interest': total_interest.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP),
        'total_principal': total_principal.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
    }


def calculate_fee(loan_amount: Decimal, fee_type: str, fee_value: Decimal, calculation_method: str) -> Decimal:
    """
    Calculate the fee amount based on the fee type and calculation method.
    
    Args:
        loan_amount: The loan amount
        fee_type: The type of fee
        fee_value: The fee value (either fixed amount or percentage)
        calculation_method: The method to calculate the fee ('fixed' or 'percentage')
        
    Returns:
        The calculated fee amount
    """
    if calculation_method == 'fixed':
        return fee_value
    elif calculation_method == 'percentage':
        return (loan_amount * fee_value / Decimal('100')).quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
    else:
        raise ValueError(f"Unknown calculation method: {calculation_method}")


def calculate_total_cost(
    loan_amount: Decimal,
    total_interest: Decimal,
    fees: List[Dict]
) -> Dict:
    """
    Calculate the total cost of a loan including principal, interest, and fees.
    
    Args:
        loan_amount: The loan amount
        total_interest: The total interest paid over the life of the loan
        fees: A list of fee dictionaries with 'amount' keys
        
    Returns:
        A dictionary with total cost breakdown
    """
    total_fees = sum(fee['amount'] for fee in fees)
    total_cost = loan_amount + total_interest + total_fees
    
    return {
        'loan_amount': loan_amount,
        'total_interest': total_interest,
        'total_fees': total_fees,
        'total_cost': total_cost
    }


def add_one_month(dt: date) -> date:
    """
    Add one month to a date, handling month end cases correctly.
    
    Args:
        dt: The starting date
        
    Returns:
        A new date one month later
    """
    month = dt.month
    year = dt.year
    
    # Move forward a month, carrying to next year if needed
    month += 1
    if month > 12:
        month = 1
        year += 1
    
    # Get the last day of the target month
    last_day = last_day_of_month(year, month)
    
    # Make sure we don't exceed the last day of the month
    day = min(dt.day, last_day)
    
    return date(year, month, day)


def last_day_of_month(year: int, month: int) -> int:
    """
    Get the last day of a given month.
    
    Args:
        year: The year
        month: The month (1-12)
        
    Returns:
        The last day of the month (28-31)
    """
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    return (next_month - timedelta(days=1)).day
