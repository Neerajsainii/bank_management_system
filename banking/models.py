from django.db import models
from django.contrib.auth.models import User
from .utils import generate_transaction_id
from django.core.exceptions import ValidationError

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    branch_code = models.CharField(max_length=10, unique=True)
    manager = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return self.name

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    designation = models.CharField(max_length=50)
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Admin"

class Employee(models.Model):
    DEPARTMENTS = (
        ('CS', 'Customer Service'),
        ('LN', 'Loans'),
        ('AC', 'Accounts'),
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    department = models.CharField(max_length=2, choices=DEPARTMENTS)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='employees')
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    managed_by_admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_employees')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_department_display()}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    customer_id = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='customers')
    created_by_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customers')
    created_by_admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customers')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('S', 'Savings'),
        ('C', 'Current'),
        ('FD', 'Fixed Deposit'),
    )
    
    account_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=2, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_accounts')
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='balance_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(interest_rate__gte=0),
                name='interest_rate_non_negative'
            )
        ]
    
    def __str__(self):
        return f"{self.account_number} - {self.get_account_type_display()}"
    
    def clean(self):
        # Additional validation beyond database constraints
        if self.balance < 0:
            raise ValidationError('Account balance cannot be negative.')
        
        if self.account_type == 'S' and hasattr(self, 'savingsaccount'):
            # For savings accounts, ensure balance >= min_balance
            savings = self.savingsaccount
            if self.balance < savings.min_balance:
                raise ValidationError(f'Savings account balance must be at least {savings.min_balance}.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class SavingsAccount(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    min_balance = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    monthly_withdrawal_limit = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return f"Savings - {self.account.account_number}"

class CurrentAccount(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    overdraft_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Current - {self.account.account_number}"

class FixedDepositAccount(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    maturity_date = models.DateField()
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    maturity_amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_period = models.PositiveIntegerField(help_text="Term period in months")
    premature_withdrawal_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Penalty percentage")
    
    def __str__(self):
        return f"Fixed Deposit - {self.account.account_number}"

class EmployeeChat(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.receiver.user.username} at {self.timestamp}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('D', 'Deposit'),
        ('W', 'Withdrawal'),
        ('T', 'Transfer'),
    )
    
    transaction_id = models.CharField(max_length=20, unique=True, default=generate_transaction_id)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_transactions')
    
    class Meta:
        ordering = ['-timestamp']
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='transaction_amount_positive'
            )
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.amount}"
    
    def clean(self):
        # Validate transaction amount is positive
        if self.amount <= 0:
            raise ValidationError('Transaction amount must be positive.')
        
        # Validate withdrawal doesn't exceed balance
        if self.transaction_type == 'W' and self.account.balance < self.amount:
            raise ValidationError('Insufficient balance for this withdrawal.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Loan(models.Model):
    LOAN_TYPES = (
        ('P', 'Personal'),
        ('H', 'Home'),
        ('A', 'Auto'),
        ('E', 'Education'),
    )
    
    LOAN_STATUS = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('C', 'Closed'),
    )
    
    loan_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=1, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField(help_text="Term period in months")
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='P')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='loans')
    
    def __str__(self):
        return f"{self.loan_id} - {self.customer} - {self.amount}"
