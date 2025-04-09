from .utils import generate_loan_id
from django.utils import timezone
from decimal import Decimal, decimal
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from .services import TransactionService
from .models import (
    Branch, Admin, Employee, Customer, Account, SavingsAccount, 
    CurrentAccount, FixedDepositAccount, Transaction, Loan, EmployeeChat
)
from .serializers import (
    BranchSerializer, AdminSerializer, EmployeeSerializer, CustomerSerializer, 
    AccountSerializer, SavingsAccountSerializer, CurrentAccountSerializer, 
    FixedDepositAccountSerializer, TransactionSerializer, LoanSerializer, EmployeeChatSerializer
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction

# Custom permissions
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return hasattr(request.user, 'admin')
        except:
            return False

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return hasattr(request.user, 'employee')
        except:
            return False

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return hasattr(request.user, 'customer')
        except:
            return False

# API Viewsets
class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
    
    @action(detail=False, methods=['get'])
    def get_subordinates(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
            subordinates = Employee.objects.filter(supervisor=employee)
            serializer = EmployeeSerializer(subordinates, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'admin'):
            return Customer.objects.all()
        elif hasattr(user, 'employee'):
            return Customer.objects.filter(branch=user.employee.branch)
        elif hasattr(user, 'customer'):
            return Customer.objects.filter(user=user)
        return Customer.objects.none()

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Account.objects.all()
        user = self.request.user
        customer_id = self.request.query_params.get('customer_id')
        
        if hasattr(user, 'admin'):
            if customer_id:
                queryset = queryset.filter(customer__customer_id=customer_id)
        elif hasattr(user, 'employee'):
            if customer_id:
                queryset = queryset.filter(customer__customer_id=customer_id, branch=user.employee.branch)
            else:
                queryset = queryset.filter(branch=user.employee.branch)
        elif hasattr(user, 'customer'):
            queryset = queryset.filter(customer=user.customer)
        else:
            queryset = Account.objects.none()
            
        return queryset

class SavingsAccountViewSet(viewsets.ModelViewSet):
    queryset = SavingsAccount.objects.all()
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]

class CurrentAccountViewSet(viewsets.ModelViewSet):
    queryset = CurrentAccount.objects.all()
    serializer_class = CurrentAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]

class FixedDepositAccountViewSet(viewsets.ModelViewSet):
    queryset = FixedDepositAccount.objects.all()
    serializer_class = FixedDepositAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]

class EmployeeChatViewSet(viewsets.ModelViewSet):
    queryset = EmployeeChat.objects.all()
    serializer_class = EmployeeChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee | IsAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
            employee = user.employee
            return EmployeeChat.objects.filter(sender=employee) | EmployeeChat.objects.filter(receiver=employee)
        return EmployeeChat.objects.none()
    
    @action(detail=False, methods=['get'])
    def unread_messages(self, request):
        user = request.user
        if hasattr(user, 'employee'):
            employee = user.employee
            unread = EmployeeChat.objects.filter(receiver=employee, is_read=False)
            serializer = EmployeeChatSerializer(unread, many=True)
            return Response(serializer.data)
        return Response({'error': 'Not an employee'}, status=status.HTTP_403_FORBIDDEN)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        user = self.request.user
        account_number = self.request.query_params.get('account_number')
        
        if hasattr(user, 'admin'):
            if account_number:
                queryset = queryset.filter(account__account_number=account_number)
        elif hasattr(user, 'employee'):
            if account_number:
                queryset = queryset.filter(account__account_number=account_number, account__branch=user.employee.branch)
            else:
                queryset = queryset.filter(account__branch=user.employee.branch)
        elif hasattr(user, 'customer'):
            if account_number:
                queryset = queryset.filter(account__account_number=account_number, account__customer=user.customer)
            else:
                accounts = Account.objects.filter(customer=user.customer)
                account_ids = [account.id for account in accounts]
                queryset = queryset.filter(account__id__in=account_ids)
        else:
            queryset = Transaction.objects.none()
            
        return queryset

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin() | IsEmployee()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Loan.objects.all()
        user = self.request.user
        customer_id = self.request.query_params.get('customer_id')
        
        if hasattr(user, 'admin'):
            if customer_id:
                queryset = queryset.filter(customer__customer_id=customer_id)
        elif hasattr(user, 'employee'):
            if customer_id:
                queryset = queryset.filter(customer__customer_id=customer_id, branch=user.employee.branch)
            else:
                queryset = queryset.filter(branch=user.employee.branch)
        elif hasattr(user, 'customer'):
            queryset = queryset.filter(customer=user.customer)
        else:
            queryset = Loan.objects.none()
            
        return queryset

# Front-end Views
def home(request):
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if hasattr(request.user, 'admin'):
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'employee'):
            return redirect('employee_dashboard')
        elif hasattr(request.user, 'customer'):
            return redirect('account_list')
    return render(request, 'banking/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            
            # Redirect based on user role
            if hasattr(user, 'admin'):
                return redirect('admin_dashboard')
            elif hasattr(user, 'employee'):
                return redirect('employee_dashboard')
            elif hasattr(user, 'customer'):
                return redirect('account_list')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'banking/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('login')


def get_interest_rate(loan_type):
    """Returns interest rate based on loan type"""
    rates = {
        'P': Decimal('12.5'),  # Personal
        'H': Decimal('8.5'),   # Home
        'A': Decimal('9.0'),   # Auto
        'E': Decimal('7.5')    # Education
    }
    return rates.get(loan_type, Decimal('10.0'))


@login_required
def account_list(request):
    try:
        customer = Customer.objects.get(user=request.user)
        accounts = Account.objects.filter(customer=customer)
        return render(request, 'banking/accounts.html', {'accounts': accounts})
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('home')

@login_required
def account_detail(request, account_number):
    account = get_object_or_404(Account, account_number=account_number)
    if account.customer.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this account.")
        return redirect('account_list')
    
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    
    # Get specific account details based on account type
    specific_account = None
    if account.account_type == 'S':
        try:
            specific_account = SavingsAccount.objects.get(account=account)
        except SavingsAccount.DoesNotExist:
            pass
    elif account.account_type == 'C':
        try:
            specific_account = CurrentAccount.objects.get(account=account)
        except CurrentAccount.DoesNotExist:
            pass
    elif account.account_type == 'F':
        try:
            specific_account = FixedDepositAccount.objects.get(account=account)
        except FixedDepositAccount.DoesNotExist:
            pass
    
    return render(request, 'banking/account_detail.html', {
        'account': account,
        'transactions': transactions,
        'specific_account': specific_account
    })


@login_required
def transfer_money(request):
    if request.method == 'POST':
        from_account_number = request.POST.get('from_account')
        to_account_number = request.POST.get('to_account')
        amount = request.POST.get('amount')
        
        try:
            from_account = Account.objects.get(account_number=from_account_number)
            to_account = Account.objects.get(account_number=to_account_number)
            amount = Decimal(amount)
            
            # Check if user owns the from_account or is an employee
            if not (request.user.is_staff or from_account.customer.user == request.user):
                messages.error(request, 'You do not have permission to transfer from this account.')
                return redirect('transfer_money')
            
            # Check if amount is positive
            if amount <= 0:
                messages.error(request, 'Amount must be positive.')
                return redirect('transfer_money')
            
            # Check if from_account has sufficient balance
            if from_account.balance < amount:
                messages.error(request, 'Insufficient balance.')
                return redirect('transfer_money')
            
            # Process the transfer within a transaction block to ensure atomicity
            with transaction.atomic():
                # Update balances
                from_account.balance -= amount
                to_account.balance += amount
                
                # Save the updated accounts
                from_account.save()
                to_account.save()
                
                # Create transaction records
                Transaction.objects.create(
                    account=from_account,
                    transaction_type='W',
                    amount=amount,
                    description=f'Transfer to {to_account.account_number}',
                    processed_by=request.user if request.user.is_staff else None
                )
                
                Transaction.objects.create(
                    account=to_account,
                    transaction_type='D',
                    amount=amount,
                    description=f'Transfer from {from_account.account_number}',
                    processed_by=request.user if request.user.is_staff else None
                )
                
                messages.success(request, f'Successfully transferred ${amount} from {from_account.account_number} to {to_account.account_number}')
                
        except Account.DoesNotExist:
            messages.error(request, 'One or both accounts do not exist.')
        except (ValueError, decimal.InvalidOperation):
            messages.error(request, 'Invalid amount format.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect('transfer_money')
    
    # Get accounts for the form
    if request.user.is_staff:
        # For staff, show all accounts
        accounts = Account.objects.all()
    else:
        # For customers, show only their accounts
        try:
            customer = Customer.objects.get(user=request.user)
            accounts = Account.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            accounts = []
    
    return render(request, 'banking/transfer_money.html', {'accounts': accounts})

@login_required
def transactions(request):
    try:
        # Get all accounts for the current user's customer
        customer_accounts = Account.objects.filter(customer__user=request.user)
        
        # Get all transactions where the user's accounts are sender OR receiver
        sent_transactions = Transaction.objects.filter(sender__in=customer_accounts)
        received_transactions = Transaction.objects.filter(receiver__in=customer_accounts)
        
        # Combine and order by timestamp
        transactions = (sent_transactions | received_transactions).order_by('-timestamp')
        
        return render(request, 'banking/transactions.html', {
            'transactions': transactions,
            'accounts': customer_accounts
        })
    
    except Exception as e:
        messages.error(request, f"Error loading transactions: {str(e)}")
        return redirect('home')
    
@login_required
@login_required
def loans(request):
    # Get current user's loans
    loans = Loan.objects.filter(customer__user=request.user).order_by('-application_date')
    
    # Get branches for dropdown
    branches = Branch.objects.all()
    
    # Get user's accounts for linking to loan
    accounts = []
    if hasattr(request.user, 'customer'):
        accounts = request.user.customer.accounts.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Validate amount
            amount = Decimal(request.POST.get('amount'))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Create loan
            loan = Loan.objects.create(
                loan_id=generate_loan_id(request.user.id),
                customer=request.user.customer,
                loan_type=request.POST.get('loan_type'),
                amount=amount,
                interest_rate=get_interest_rate(request.POST.get('loan_type')),
                term_period=int(request.POST.get('term_period')),
                branch=Branch.objects.get(id=request.POST.get('branch')),
                linked_account=Account.objects.get(
                    account_number=request.POST.get('account'),
                    customer=request.user.customer
                ),
                application_date=timezone.now().date()
            )
            
            messages.success(request, "Loan application submitted successfully!")
            return redirect('loans')
            
        except Account.DoesNotExist:
            messages.error(request, "Selected account not found or doesn't belong to you")
        except Branch.DoesNotExist:
            messages.error(request, "Selected branch not found")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error submitting application: {str(e)}")
    
    return render(request, 'banking/loans.html', {
        'loans': loans,
        'branches': branches,
        'accounts': accounts,
        'loan_types': Loan.LOAN_TYPES  # Pass loan types to template
    })

def get_interest_rate(loan_type):
    # Implement your interest rate logic here
    rates = {
        'P': 12.5,  # Personal
        'H': 8.5,   # Home
        'A': 9.0,    # Auto
        'E': 7.5     # Education
    }
    return rates.get(loan_type, 10.0)
@login_required
def employee_dashboard(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    employee = request.user.employee
    customers = Customer.objects.filter(branch=employee.branch)
    accounts = Account.objects.filter(branch=employee.branch)
    loans = Loan.objects.filter(branch=employee.branch)
    
    context = {
        'employee': employee,
        'customers_count': customers.count(),
        'accounts_count': accounts.count(),
        'loans_count': loans.count(),
        'pending_loans': loans.filter(status='P').count()
    }
    
    return render(request, 'banking/employee_dashboard.html', context)

@login_required
def employee_customers(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    employee = request.user.employee
    customers = Customer.objects.filter(branch=employee.branch)
    
    # Handle customer creation
    if request.method == 'POST':
        from django.contrib.auth.models import User
        import random
        import string
        
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            customer_id = request.POST.get('customer_id')
            date_of_birth = request.POST.get('date_of_birth')
            address = request.POST.get('address')
            username = request.POST.get('username')
            password = request.POST.get('password')
            branch_id = request.POST.get('branch')
            
            # Create the user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Get the branch
            branch = Branch.objects.get(id=branch_id)
            
            # Create the customer record
            customer = Customer.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth,
                customer_id=customer_id,
                branch=branch,
                created_by_employee=employee
            )
            
            # Check if we need to create an account for this customer
            create_account = request.POST.get('create_account') == 'on'
            if create_account:
                account_type = request.POST.get('account_type')
                initial_deposit = request.POST.get('initial_deposit')
                
                # Generate a unique account number
                account_number = f"AC{random.randint(100000, 999999)}"
                while Account.objects.filter(account_number=account_number).exists():
                    account_number = f"AC{random.randint(100000, 999999)}"
                
                # Create the basic account
                account = Account.objects.create(
                    account_number=account_number,
                    customer=customer,
                    account_type=account_type,
                    balance=initial_deposit,
                    is_active=True,
                    branch=branch,
                    created_by_employee=employee
                )
                
                # Create the specific account type
                if account_type == 'S':
                    # Savings account
                    SavingsAccount.objects.create(
                        account=account,
                        min_balance=500,
                        interest_rate=4.5
                    )
                    account.interest_rate = 4.5
                    account.save()
                elif account_type == 'C':
                    # Current account
                    CurrentAccount.objects.create(
                        account=account,
                        overdraft_limit=1000
                    )
                elif account_type == 'FD':
                    # Fixed deposit account
                    from datetime import datetime, timedelta
                    term_period = 12  # Default to 12 months
                    maturity_date = datetime.now().date() + timedelta(days=term_period * 30)
                    interest_rate = 6.0
                    
                    deposit_amount = float(initial_deposit)
                    interest = deposit_amount * (interest_rate / 100) * (term_period / 12)
                    maturity_amount = deposit_amount + interest
                    
                    FixedDepositAccount.objects.create(
                        account=account,
                        maturity_date=maturity_date,
                        deposit_amount=deposit_amount,
                        maturity_amount=maturity_amount,
                        term_period=term_period,
                        premature_withdrawal_penalty=1.0
                    )
                    account.interest_rate = interest_rate
                    account.save()
                
                messages.success(request, f"Customer '{first_name} {last_name}' created successfully with a new {account.get_account_type_display()} account.")
            else:
                messages.success(request, f"Customer '{first_name} {last_name}' created successfully.")
            
            # Refresh customers after creation
            customers = Customer.objects.filter(branch=employee.branch)
            
        except Exception as e:
            messages.error(request, f"Error creating customer: {str(e)}")
    
    return render(request, 'banking/employee_customers.html', {'customers': customers, 'employee': employee})

@login_required
def employee_chat(request):
    if not hasattr(request.user, 'employee') and not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    if hasattr(request.user, 'employee'):
        employee = request.user.employee
        branch_employees = Employee.objects.filter(branch=employee.branch).exclude(id=employee.id)
        
        # Mark messages as read
        EmployeeChat.objects.filter(receiver=employee, is_read=False).update(is_read=True)
        
        chats = EmployeeChat.objects.filter(sender=employee) | EmployeeChat.objects.filter(receiver=employee)
        chats = chats.order_by('timestamp')
        
        context = {
            'employee': employee,
            'branch_employees': branch_employees,
            'chats': chats
        }
        
        return render(request, 'banking/employee_chat.html', context)
    
    # For admin users
    branches = Branch.objects.all()
    return render(request, 'banking/admin_employee_chat.html', {'branches': branches})

@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    admin = request.user.admin
    branches = Branch.objects.all()
    employees = Employee.objects.all()
    customers = Customer.objects.all()
    accounts = Account.objects.all()
    loans = Loan.objects.all()
    
    # Handle branch creation form submission
    if request.method == 'POST' and 'branch_code' in request.POST:
        name = request.POST.get('name')
        branch_code = request.POST.get('branch_code')
        address = request.POST.get('address')
        manager = request.POST.get('manager')
        phone = request.POST.get('phone')
        
        # Create a new branch
        Branch.objects.create(
            name=name,
            branch_code=branch_code,
            address=address,
            manager=manager,
            phone=phone
        )
        
        messages.success(request, f"Branch '{name}' created successfully.")
        # Refresh branches after creation
        branches = Branch.objects.all()
    
    # Handle employee creation form submission
    elif request.method == 'POST' and 'employee_id' in request.POST and 'first_name' in request.POST:
        from django.contrib.auth.models import User
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        employee_id = request.POST.get('employee_id')
        department = request.POST.get('department')
        date_of_birth = request.POST.get('date_of_birth')
        branch_id = request.POST.get('branch')
        salary = request.POST.get('salary')
        supervisor_id = request.POST.get('supervisor')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        
        try:
            # Create a user account (generate a temporary password)
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Make username unique if it already exists
            count = 1
            temp_username = username
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{username}{count}"
                count += 1
            username = temp_username
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create the employee record
            branch = Branch.objects.get(id=branch_id) if branch_id else None
            supervisor = Employee.objects.get(id=supervisor_id) if supervisor_id else None
            
            Employee.objects.create(
                user=user,
                employee_id=employee_id,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth,
                department=department,
                salary=salary,
                branch=branch,
                supervisor=supervisor,
                managed_by_admin=admin
            )
            
            messages.success(request, f"Employee '{first_name} {last_name}' created successfully. Username: {username}, Temporary Password: {temp_password}")
            
            # Store the temporary password in session
            if 'temp_passwords' not in request.session:
                request.session['temp_passwords'] = {}
            request.session['temp_passwords'][username] = temp_password
            request.session.modified = True
            
            # Refresh employees after creation
            employees = Employee.objects.all()
        except Exception as e:
            messages.error(request, f"Error creating employee: {str(e)}")
    
    # Handle password reset
    elif request.method == 'POST' and 'action' in request.POST and request.POST['action'] == 'reset_password':
        from django.contrib.auth.models import User
        import random
        import string
        
        try:
            employee_id = request.POST.get('employee_id')
            employee = Employee.objects.get(id=employee_id)
            user = employee.user
            
            # Generate a new temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Update user's password
            user.set_password(temp_password)
            user.save()
            
            # Store the temporary password in session
            if 'temp_passwords' not in request.session:
                request.session['temp_passwords'] = {}
            request.session['temp_passwords'][user.username] = temp_password
            request.session.modified = True
            
            messages.success(request, f"Password for {user.first_name} {user.last_name} reset successfully. New password: {temp_password}")
            
        except Exception as e:
            messages.error(request, f"Error resetting password: {str(e)}")
    
    # Handle branch edit
    elif request.method == 'POST' and 'action' in request.POST and request.POST['action'] == 'edit_branch':
        try:
            branch_id = request.POST.get('branch_id')
            branch = Branch.objects.get(id=branch_id)
            
            # Update branch details
            branch.name = request.POST.get('name')
            branch.branch_code = request.POST.get('branch_code')
            branch.address = request.POST.get('address')
            branch.manager = request.POST.get('manager')
            branch.phone = request.POST.get('phone')
            branch.save()
            
            messages.success(request, f"Branch '{branch.name}' updated successfully.")
            # Refresh branches after update
            branches = Branch.objects.all()
        except Exception as e:
            messages.error(request, f"Error updating branch: {str(e)}")
    
    # Handle branch delete
    elif request.method == 'POST' and 'action' in request.POST and request.POST['action'] == 'delete_branch':
        try:
            branch_id = request.POST.get('branch_id')
            branch = Branch.objects.get(id=branch_id)
            branch_name = branch.name
            
            # Check if branch has employees or customers
            if branch.employees.count() > 0 or branch.customers.count() > 0:
                messages.error(request, f"Cannot delete branch '{branch_name}' as it has associated employees or customers.")
            else:
                branch.delete()
                messages.success(request, f"Branch '{branch_name}' deleted successfully.")
            
            # Refresh branches after deletion
            branches = Branch.objects.all()
        except Exception as e:
            messages.error(request, f"Error deleting branch: {str(e)}")
    
    context = {
        'admin': admin,
        'branches': branches,
        'branches_count': branches.count(),
        'employees': employees,
        'employees_count': employees.count(),
        'customers_count': customers.count(),
        'accounts_count': accounts.count(),
        'loans_count': loans.count(),
        'pending_loans': loans.filter(status='P').count()
    }
    
    return render(request, 'banking/admin_dashboard.html', context)

@login_required
def admin_branches(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    branches = Branch.objects.all()
    
    context = {
        'branches': branches
    }
    
    return render(request, 'banking/admin_branches.html', context)

@login_required
def admin_employees(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    employees = Employee.objects.all().select_related('user', 'branch', 'supervisor')
    branches = Branch.objects.all()
    
    # Get temporary passwords if they exist in session
    temp_passwords = {}
    if 'temp_passwords' in request.session:
        temp_passwords = request.session['temp_passwords']
    
    context = {
        'employees': employees,
        'temp_passwords': temp_passwords,
        'branches': branches
    }
    
    return render(request, 'banking/admin_employees.html', context)

@login_required
def admin_customers(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    customers = Customer.objects.all().select_related('user', 'branch')
    
    context = {
        'customers': customers
    }
    
    return render(request, 'banking/admin_customers.html', context)

@login_required
def admin_accounts(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    accounts = Account.objects.all().select_related('customer', 'branch')
    
    context = {
        'accounts': accounts
    }
    
    return render(request, 'banking/admin_accounts.html', context)

@login_required
def employee_accounts(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    employee = request.user.employee
    accounts = Account.objects.filter(branch=employee.branch)
    
    context = {
        'employee': employee,
        'accounts': accounts
    }
    
    return render(request, 'banking/employee_accounts.html', context)

@login_required
def employee_transactions(request):
    # Check if user is an employee
    try:
        employee = Employee.objects.get(user=request.user)
        branch = employee.branch
    except Employee.DoesNotExist:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        
        try:
            account = Account.objects.get(id=account_id)
            amount = Decimal(amount)
            
            # Check if amount is positive
            if amount <= 0:
                messages.error(request, 'Amount must be positive.')
                return redirect('employee_transactions')
            
            # Process the transaction within a transaction block to ensure atomicity
            with transaction.atomic():
                if transaction_type == 'D':  # Deposit
                    account.balance += amount
                    account.save()
                    
                    Transaction.objects.create(
                        account=account,
                        transaction_type='D',
                        amount=amount,
                        description=description or 'Deposit',
                        processed_by=request.user
                    )
                    
                    messages.success(request, f'Successfully deposited ${amount} to account {account.account_number}')
                    
                elif transaction_type == 'W':  # Withdrawal
                    # Check if account has sufficient balance
                    if account.balance < amount:
                        messages.error(request, 'Insufficient balance.')
                        return redirect('employee_transactions')
                    
                    account.balance -= amount
                    account.save()
                    
                    Transaction.objects.create(
                        account=account,
                        transaction_type='W',
                        amount=amount,
                        description=description or 'Withdrawal',
                        processed_by=request.user
                    )
                    
                    messages.success(request, f'Successfully withdrew ${amount} from account {account.account_number}')
                
        except Account.DoesNotExist:
            messages.error(request, 'Account does not exist.')
        except (ValueError, decimal.InvalidOperation):
            messages.error(request, 'Invalid amount format.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect('employee_transactions')
    
    # Get transactions for the branch
    transactions = Transaction.objects.filter(account__branch=branch).order_by('-timestamp')
    
    context = {
        'employee': employee,
        'transactions': transactions,
    }
    
    return render(request, 'banking/employee_transactions.html', context)

@login_required
def employee_loans(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    employee = request.user.employee
    loans = Loan.objects.filter(branch=employee.branch)
    
    # Handle loan approval/rejection
    if request.method == 'POST' and 'loan_id' in request.POST:
        loan_id = request.POST.get('loan_id')
        action = request.POST.get('action')
        
        try:
            loan = Loan.objects.get(loan_id=loan_id, branch=employee.branch)
            
            if action == 'approve':
                loan.status = 'A'
                loan.approved_by = employee
                messages.success(request, f"Loan {loan_id} has been approved.")
            elif action == 'reject':
                loan.status = 'R'
                messages.success(request, f"Loan {loan_id} has been rejected.")
            
            loan.save()
            
        except Exception as e:
            messages.error(request, f"Error processing loan: {str(e)}")
        
        # Refresh loans after processing
        loans = Loan.objects.filter(branch=employee.branch)
    
    context = {
        'employee': employee,
        'loans': loans,
        'pending_loans': loans.filter(status='P').count()
    }
    
    return render(request, 'banking/employee_loans.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('change_password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('change_password')
        
        # Check password strength
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('change_password')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Your password has been changed successfully.")
        
        # Redirect based on user role
        if hasattr(request.user, 'admin'):
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'employee'):
            return redirect('employee_dashboard')
        else:
            return redirect('account_list')
    
    return render(request, 'banking/change_password.html')
