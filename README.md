# Bank Management System

A comprehensive banking management system built with Django, featuring role-based access control for administrators, employees, and customers.

## Features

- **Multi-role System**
  - Admin Panel
  - Employee Dashboard
  - Customer Portal

- **Account Management**
  - Savings Accounts
  - Current Accounts
  - Fixed Deposit Accounts

- **Transaction System**
  - Deposits
  - Withdrawals
  - Transfers
  - Transaction History

- **Loan Management**
  - Loan Applications
  - Approval Workflow
  - Loan Tracking

- **Customer Management**
  - Customer Registration
  - Account Creation
  - Profile Management

- **Employee Features**
  - Customer Management
  - Transaction Processing
  - Loan Approval
  - Internal Chat System

## Technology Stack

- Python 3.x
- Django 5.1.7
- Bootstrap 5
- SQLite (Development)
- PostgreSQL (Production)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bank-management-system.git
cd bank-management-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
bank-management-system/
├── banking/                 # Main application
│   ├── templates/          # HTML templates
│   ├── static/            # Static files
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   └── urls.py            # URL configurations
├── bankingsystem/         # Project settings
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Bootstrap Framework
- Python Community

## ER Model

The system includes the following entities:

1. **Branch** - Represents bank branches
   - Fields: name, address, branch_code, manager, phone

2. **Admin** - Represents system administrators
   - Fields: user (linked to Django User), admin_id, phone_number, designation, date_joined

3. **Employee** - Represents bank employees
   - Fields: user, employee_id, phone_number, address, date_of_birth, department, salary, date_joined, branch, supervisor, managed_by_admin

4. **Customer** - Represents bank customers
   - Fields: user, phone_number, address, date_of_birth, customer_id, branch, created_by_employee, created_by_admin

5. **Account** - Represents different types of bank accounts
   - Fields: account_number, customer, account_type, balance, created_at, is_active, interest_rate, branch, created_by_employee

6. **SavingsAccount** - Specific details for savings accounts
   - Fields: account (linked to Account), min_balance, monthly_withdrawal_limit

7. **CurrentAccount** - Specific details for current accounts
   - Fields: account (linked to Account), overdraft_limit

8. **FixedDepositAccount** - Specific details for fixed deposit accounts
   - Fields: account (linked to Account), maturity_date, deposit_amount, maturity_amount, term_period, premature_withdrawal_penalty

9. **Transaction** - Represents financial transactions
   - Fields: transaction_id, account, transaction_type, amount, timestamp, destination_account, description, processed_by_employee, payment_gateway

10. **Loan** - Represents loan applications and approvals
    - Fields: loan_id, customer, loan_type, amount, interest_rate, term_period, application_date, status, approved_by, branch

11. **EmployeeChat** - Represents chat messages between employees
    - Fields: sender, receiver, message, timestamp, is_read

## Role-Based Access Control

The system implements three levels of access:

1. **Admin**
   - Create/manage branches
   - Create/manage employees
   - Create/manage customers
   - View all system data
   - System configuration

2. **Employee**
   - Create/manage customers (within assigned branch)
   - Process transactions
   - Review loan applications
   - View branch-specific data
   - Chat with other employees

3. **Customer**
   - View own accounts
   - Perform transactions
   - Apply for loans
   - View transaction history

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Migrate the database:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
5. Run the server:
   ```
   python manage.py runserver
   ```

## API Endpoints

- `/api/branches/` - Branch operations
- `/api/admins/` - Admin operations
- `/api/employees/` - Employee operations
- `/api/customers/` - Customer operations
- `/api/accounts/` - Account operations
- `/api/savings-accounts/` - Savings account operations
- `/api/current-accounts/` - Current account operations
- `/api/fixed-deposit-accounts/` - Fixed deposit account operations
- `/api/transactions/` - Transaction operations
- `/api/loans/` - Loan operations
- `/api/employee-chats/` - Employee chat operations

## Frontend Pages

### Customer Pages
- `/` - Home page
- `/accounts/` - View all accounts
- `/accounts/<account_number>/` - Account details
- `/transactions/` - View transactions
- `/loans/` - View loans

### Employee Pages
- `/employee/dashboard/` - Employee dashboard
- `/employee/customers/` - View and manage customers
- `/employee/chat/` - Employee chat system

### Admin Pages
- `/admin/dashboard/` - Admin dashboard

## Future Enhancements

- Payment gateway integration
- Mobile banking features
- Customer support ticket system
- Financial analytics and reporting
- Account statements and tax documents

## Technologies Used

- Django
- Django REST Framework
- Bootstrap 5
- SQLite (default, can be changed to other databases)

## License

This project is licensed under the MIT License. 