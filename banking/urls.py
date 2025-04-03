from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # API ViewSets
    BranchViewSet, AdminViewSet, EmployeeViewSet, CustomerViewSet, 
    AccountViewSet, SavingsAccountViewSet, CurrentAccountViewSet, 
    FixedDepositAccountViewSet, TransactionViewSet, LoanViewSet, 
    EmployeeChatViewSet,
    
    # Frontend Views
    home, account_list, account_detail, transactions, transfer_money, loans,
    employee_dashboard, employee_customers, employee_chat, admin_dashboard,
    login_view, logout_view,
    
    # Admin Views
    admin_branches, admin_employees, admin_customers, admin_accounts,
    
    # Employee Views
    employee_accounts, employee_transactions, employee_loans, change_password
)

router = DefaultRouter()
# API Router Registration
router.register(r'branches', BranchViewSet)
router.register(r'admins', AdminViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'savings-accounts', SavingsAccountViewSet)
router.register(r'current-accounts', CurrentAccountViewSet)
router.register(r'fixed-deposit-accounts', FixedDepositAccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'employee-chats', EmployeeChatViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Frontend URLs - Customer
    path('', home, name='home'),
    path('accounts/', account_list, name='account_list'),
    path('accounts/<str:account_number>/', account_detail, name='account_detail'),
    path('loans/', loans, name='loans'),
    path('transfer/', transfer_money, name='transfer_money'),
    path('history/', transactions, name='transactions'),
    
    # Frontend URLs - Employee
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employee/customers/', employee_customers, name='employee_customers'),
    path('employee/accounts/', employee_accounts, name='employee_accounts'),
    path('employee/transactions/', employee_transactions, name='employee_transactions'),
    path('employee/loans/', employee_loans, name='employee_loans'),
    path('employee/chat/', employee_chat, name='employee_chat'),
    
    # Frontend URLs - Admin
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/branches/', admin_branches, name='admin_branches'),
    path('admin/employees/', admin_employees, name='admin_employees'),
    path('admin/customers/', admin_customers, name='admin_customers'),
    path('admin/accounts/', admin_accounts, name='admin_accounts'),
    
    # User Account URLs
    path('change-password/', change_password, name='change_password'),
] 