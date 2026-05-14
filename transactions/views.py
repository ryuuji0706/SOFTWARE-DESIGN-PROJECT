from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Bill, Transaction, Budget

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

def budget_view(request):
    # 1. Fetch user budgets (Convert them into a dictionary for easy lookup)
    user_budgets = {b.category_name: b.limit for b in Budget.objects.all()}
    
    # 2. Setup Month Filtering (JS months are 0-11, Django is 1-12)
    selected_month = request.GET.get('month', 'all')
    base_query = Transaction.objects.filter(type='EXPENSE')
    if selected_month != 'all':
        base_query = base_query.filter(transaction_date__month=int(selected_month) + 1)

    # 3. Calculate spent per category using the same logic as Analytics
    spent_data = {
        'Food': base_query.filter(Q(description__icontains='food') | Q(description__icontains='meal')).aggregate(total=Sum('amount'))['total'] or 0,
        'Transport': base_query.filter(Q(description__icontains='transport') | Q(description__icontains='gas')).aggregate(total=Sum('amount'))['total'] or 0,
        'Health': base_query.filter(description__icontains='health').aggregate(total=Sum('amount'))['total'] or 0,
        'Utilities': base_query.filter(Q(description__icontains='electric') | Q(description__icontains='water') | Q(description__icontains='internet') | Q(description__icontains='utility')).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Shopping is the fallback for any unmapped expenses
    total_expense = base_query.aggregate(total=Sum('amount'))['total'] or 0
    shopping_spent = total_expense - sum(spent_data.values())
    spent_data['Shopping'] = shopping_spent if shopping_spent > 0 else 0

    # 4. Process the data for the HTML Template
    categories_info = []
    g_count = w_count = b_count = 0

    for cat_name in ['Food', 'Transport', 'Utilities', 'Shopping', 'Health']:
        limit = user_budgets.get(cat_name, 1000) # Default to 1000 if not set
        spent = spent_data[cat_name]
        percent = (spent / limit) * 100 if limit > 0 else 0
        
        # Status
        if percent >= 100:
            cls, label = "bad", "Over"
            b_count += 1
        elif percent >= 70:
            cls, label = "warn", "Warning"
            w_count += 1
        else:
            cls, label = "good", "Good"
            g_count += 1

        # Dynamic Suggestions
        if percent < 50: suggestion = "Good control"
        elif cat_name == "Food": suggestion = "Cook at home"
        elif cat_name == "Transport": suggestion = "Use public transport"
        elif cat_name == "Utilities": suggestion = "Save electricity"
        elif cat_name == "Shopping": suggestion = "Avoid impulse buying"
        elif cat_name == "Health": suggestion = "Compare clinics"
        else: suggestion = "Monitor spending"

        categories_info.append({
            'name': cat_name,
            'spent': spent,
            'limit': limit,
            'percent': min(percent, 100), # Caps progress bar visually at 100%
            'cls': cls,
            'label': label,
            'suggestion': suggestion
        })

    context = {
        'categories_info': categories_info,
        'good': g_count,
        'warn': w_count,
        'bad': b_count,
        'selected_month': selected_month
    }
    return render(request, 'transactions/budget.html', context)


def set_budget(request):
    if request.method == 'POST':
        cat = request.POST.get('cat')
        amount = request.POST.get('amount')
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        # update_or_create means if a budget already exists for Food, it updates it. If not, it creates it!
        Budget.objects.update_or_create(
            user=user,
            category_name=cat,
            defaults={'limit': amount}
        )
    return redirect('budget')

# --- NEW PLACEHOLDER VIEWS ---

def expenses_view(request):
    # Placeholder for the expenses page
    return render(request, 'analytics/expenses.html')