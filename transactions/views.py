from datetime import date
from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Bill, Transaction, Budget
from django.contrib.auth.decorators import login_required

# ==========================================
# BILLS VIEWS
# ==========================================

@login_required
def bills_view(request):
    bills = Bill.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bills': bills,
        'total': bills.count(),
        'paid': bills.filter(status='Paid').count(),
        'unpaid': bills.filter(status='Unpaid').count(),
        'overdue': bills.filter(status='Overdue').count(),
    }
    return render(request, 'transactions/bills.html', context)

@login_required
def add_bill(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        due = request.POST.get('due')
        
        # Secured: Saves directly to the logged-in user
        Bill.objects.create(user=request.user, name=name, amount=amount, due_date=due, status='Unpaid')
        
    return redirect('bills')

@login_required
def update_bill(request, bill_id, new_status):
    if request.method == 'POST':
        # Secured: Ensures they can only update THEIR bills
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        bill.status = new_status
        bill.save()
    return redirect('bills')

@login_required
def delete_bill(request, bill_id):
    if request.method == 'POST':
        # Secured: Ensures they can only delete THEIR bills
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        bill.delete()
    return redirect('bills')

# --- NEW: EDIT BILL (Option A) ---
@login_required
def edit_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    
    if request.method == 'POST':
        bill.name = request.POST.get('name', bill.name)
        bill.amount = request.POST.get('amount', bill.amount)
        bill.due_date = request.POST.get('due', bill.due_date)
        bill.save()
        return redirect('bills')
        
    # If using a dedicated edit page. If using modals, you might just use POST.
    return render(request, 'transactions/edit_bill.html', {'bill': bill})


# ==========================================
# TRANSACTIONS VIEWS
# ==========================================

@login_required
def transaction_list(request):
    user_txns = Transaction.objects.filter(user=request.user)
    transactions = user_txns.order_by('-transaction_date')[:10]

    total_income = user_txns.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = user_txns.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    net = total_income - total_expense

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net': net,
    }
    return render(request, 'transactions/transactions.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        desc = request.POST.get('desc')
        amount = request.POST.get('amount')
        txn_type = request.POST.get('type') 
        
        # Secured: Single clean version tied directly to the user
        Transaction.objects.create(
            user=request.user,
            description=desc,
            amount=amount,
            type=txn_type,
            transaction_date=date.today()
        )
    return redirect('transaction_list')

# --- NEW: DELETE TRANSACTION (Option A) ---
@login_required
def delete_transaction(request, transaction_id):
    if request.method == 'POST':
        # Secured lookup before deletion
        txn = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        txn.delete()
    return redirect('transaction_list')


# ==========================================
# BUDGET VIEWS
# ==========================================

@login_required
def budget_view(request):
    user_budgets = {b.category_name: b.limit for b in Budget.objects.filter(user=request.user)}
    
    selected_month = request.GET.get('month', 'all')
    
    # FIXED PRIVACY LEAK: Now safely filters by user=request.user
    base_query = Transaction.objects.filter(user=request.user, type='EXPENSE')
    
    if selected_month != 'all':
        base_query = base_query.filter(transaction_date__month=int(selected_month) + 1)

    spent_data = {
        'Food': base_query.filter(Q(description__icontains='food') | Q(description__icontains='meal')).aggregate(total=Sum('amount'))['total'] or 0,
        'Transport': base_query.filter(Q(description__icontains='transport') | Q(description__icontains='gas')).aggregate(total=Sum('amount'))['total'] or 0,
        'Health': base_query.filter(description__icontains='health').aggregate(total=Sum('amount'))['total'] or 0,
        'Utilities': base_query.filter(Q(description__icontains='electric') | Q(description__icontains='water') | Q(description__icontains='internet') | Q(description__icontains='utility')).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    total_expense = base_query.aggregate(total=Sum('amount'))['total'] or 0
    shopping_spent = total_expense - sum(spent_data.values())
    spent_data['Shopping'] = shopping_spent if shopping_spent > 0 else 0

    categories_info = []
    g_count = w_count = b_count = 0

    for cat_name in ['Food', 'Transport', 'Utilities', 'Shopping', 'Health']:
        limit = user_budgets.get(cat_name, 1000)
        spent = spent_data[cat_name]
        percent = (spent / limit) * 100 if limit > 0 else 0
        
        if percent >= 100:
            cls, label = "bad", "Over"
            b_count += 1
        elif percent >= 70:
            cls, label = "warn", "Warning"
            w_count += 1
        else:
            cls, label = "good", "Good"
            g_count += 1

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
            'percent': min(percent, 100),
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

@login_required
def set_budget(request):
    if request.method == 'POST':
        cat = request.POST.get('cat')
        amount = request.POST.get('amount')
        
        # Secured: Removed the User.objects.first() fallback
        Budget.objects.update_or_create(
            user=request.user,
            category_name=cat,
            defaults={'limit': amount}
        )
    return redirect('budget')

@login_required
def expenses_view(request):
    return render(request, 'analytics/expenses.html')