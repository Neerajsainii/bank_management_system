from django.db import transaction
from .models import Account, Transaction
from decimal import Decimal

class TransactionService:
    @staticmethod
    def transfer(sender_account, receiver_account, amount, description=""):
        # Validate amount
        if amount <= Decimal('0'):
            return None, "Amount must be positive"
            
        # Check if sender has sufficient balance
        if sender_account.balance < amount:
            return None, "Insufficient balance"

        # Create transaction record (initially PENDING)
        new_transaction = Transaction.objects.create(
            sender=sender_account,
            receiver=receiver_account,
            amount=amount,
            transaction_type='T',
            description=description,
            status='PENDING'
        )

        # Perform balance update in a database transaction
        try:
            with transaction.atomic():
                # Deduct from sender
                sender_account.balance -= amount
                sender_account.save()

                # Add to receiver
                receiver_account.balance += amount
                receiver_account.save()

                # Update transaction status to SUCCESS
                new_transaction.status = 'SUCCESS'
                new_transaction.save()

            return new_transaction, "Transfer successful"
        
        except Exception as e:
            # If any error occurs, mark as FAILED
            new_transaction.status = 'FAILED'
            new_transaction.save()
            return None, f"Transfer failed: {str(e)}"