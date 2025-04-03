from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using its key."""
    return dictionary.get(key, '') 

@register.filter
def filter_pending(loans):
    return [loan for loan in loans if loan.status == 'P']

@register.filter
def monthly_payment(principal, args):
    """Calculate monthly payment for a loan
    Usage: {{ principal|monthly_payment:'interest_rate,term_period' }}
    """
    if not args or ',' not in args:
        return 0
    
    try:
        interest_rate, term_period = args.split(',')
        interest_rate = Decimal(interest_rate.strip())
        term_period = int(term_period.strip())
        
        if term_period == 0 or interest_rate == 0:
            return principal / term_period if term_period > 0 else 0
        
        # Convert annual interest rate to monthly
        monthly_rate = interest_rate / 100 / 12
        
        # Calculate monthly payment using the formula: P * r * (1 + r)^n / ((1 + r)^n - 1)
        numerator = monthly_rate * (1 + monthly_rate) ** term_period
        denominator = (1 + monthly_rate) ** term_period - 1
        
        if denominator == 0:
            return 0
        
        monthly = principal * (numerator / denominator)
        return round(monthly, 2)
    except Exception:
        return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value

@register.filter
def add(value, arg):
    """Add the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value 