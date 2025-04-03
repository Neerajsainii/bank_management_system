import random
import string
from datetime import datetime
from django.utils import timezone

def generate_transaction_id():
    # Example: "TXN20240403ABC123"
    date_str = datetime.now().strftime("%Y%m%d")
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN{date_str}{rand_str}"

def generate_loan_id(user_id):
    """Generate unique loan ID: LN{user_id}{timestamp}{random_string}"""
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"LN{user_id}{timestamp}{rand_str}"