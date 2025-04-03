from django.contrib import admin
from .models import (
    Branch, Admin, Employee, Customer, Account, SavingsAccount, 
    CurrentAccount, FixedDepositAccount, Transaction, Loan, EmployeeChat
)

admin.site.register(Branch)
admin.site.register(Admin)
admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(SavingsAccount)
admin.site.register(CurrentAccount)
admin.site.register(FixedDepositAccount)
admin.site.register(Transaction)
admin.site.register(Loan)
admin.site.register(EmployeeChat)
