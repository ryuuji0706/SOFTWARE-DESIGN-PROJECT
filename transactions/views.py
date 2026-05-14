from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Bill, Transaction

def bills_view(request):
    # Fetch all bills from the database
    bills = Bill.objects.all().order_by('-created_at')
    
    # --- ADD THESE TWO LINES ---
    print("BILLS FOUND:", bills) 
    print("TOTAL COUNT:", bills.count())
    # ---------------------------
    
    context = {
        'bills': bills,
        'total': bills.count(),
        'paid': bills.filter(status='Paid').count(),
        'unpaid': bills.filter(status='Unpaid').count(),
        'overdue': bills.filter(status='Overdue').count(),
    }
    return render(request, 'transactions/bills.html', context)

def add_bill(request):
    if request.method == 'POST':
        # Grab data from the HTML form
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        due = request.POST.get('due')
        
        # Temporarily assign to the first user if authentication isn't fully built yet
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        # Save to database
        Bill.objects.create(user=user, name=name, amount=amount, due_date=due, status='Unpaid')
        
    return redirect('bills')

def update_bill(request, bill_id, new_status):
    if request.method == 'POST':
        bill = Bill.objects.get(id=bill_id)
        bill.status = new_status
        bill.save()
    return redirect('bills')

def delete_bill(request, bill_id):
    if request.method == 'POST':
        Bill.objects.get(id=bill_id).delete()
    return redirect('bills')

# ... Keep your existing transaction_list, add_transaction, and expenses_view here ...

def transaction_list(request):
    # Fetch latest 10 transactions
    transactions = Transaction.objects.all().order_by('-created_at')[:10]

    # Calculate totals using Django's database aggregate functions
    income_query = Transaction.objects.filter(type='INCOME').aggregate(total=Sum('amount'))
    total_income = income_query['total'] or 0

    expense_query = Transaction.objects.filter(type='EXPENSE').aggregate(total=Sum('amount'))
    total_expense = expense_query['total'] or 0

    net = total_income - total_expense

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net': net,
    }
    # Make sure this matches where you save the HTML file!
    return render(request, 'transactions/transactions.html', context)

def add_transaction(request):
    if request.method == 'POST':
        desc = request.POST.get('desc')
        amount = request.POST.get('amount')
        txn_type = request.POST.get('type') # Will grab 'INCOME' or 'EXPENSE' from the form
        
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        # We use today's date automatically since it isn't in your form UI
        Transaction.objects.create(
            user=user,
            description=desc,
            amount=amount,
            type=txn_type,
            transaction_date=date.today()
        )
    return redirect('transaction_list')

# --- NEW PLACEHOLDER VIEWS ---

def expenses_view(request):
    # Placeholder for the expenses page
    return render(request, 'analytics/expenses.html')