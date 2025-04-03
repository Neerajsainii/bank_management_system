from rest_framework import serializers
from .models import (
    Branch, Admin, Employee, Customer, Account, SavingsAccount, 
    CurrentAccount, FixedDepositAccount, Transaction, Loan, EmployeeChat
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Admin
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    supervisor_name = serializers.StringRelatedField(source='supervisor', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    created_by_employee_name = serializers.StringRelatedField(source='created_by_employee', read_only=True)
    created_by_admin_name = serializers.StringRelatedField(source='created_by_admin', read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.StringRelatedField(source='customer', read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    
    class Meta:
        model = Account
        fields = '__all__'

class SavingsAccountSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)
    
    class Meta:
        model = SavingsAccount
        fields = '__all__'

class CurrentAccountSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)
    
    class Meta:
        model = CurrentAccount
        fields = '__all__'

class FixedDepositAccountSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)
    
    class Meta:
        model = FixedDepositAccount
        fields = '__all__'

class EmployeeChatSerializer(serializers.ModelSerializer):
    sender_name = serializers.StringRelatedField(source='sender', read_only=True)
    receiver_name = serializers.StringRelatedField(source='receiver', read_only=True)
    
    class Meta:
        model = EmployeeChat
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    account_number = serializers.StringRelatedField(source='account.account_number', read_only=True)
    destination_account_number = serializers.StringRelatedField(source='destination_account.account_number', read_only=True)
    processed_by_employee_name = serializers.StringRelatedField(source='processed_by_employee', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.StringRelatedField(source='customer', read_only=True)
    approved_by_name = serializers.StringRelatedField(source='approved_by', read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__' 