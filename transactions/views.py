from datetime import datetime, date
import calendar
from urllib import request
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Bill, Transaction, Budget, Category
from django.contrib.auth.decorators import login_required

# --- HELPER FUNCTION: Safely adds 1 month to a date ---
def add_one_month(orig_date):
    month = orig_date.month - 1 + 1
    year = orig_date.year + month // 12
    month = month % 12 + 1
    day = min(orig_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


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
        is_monthly = request.POST.get('is_monthly') == 'true'
        category_name = request.POST.get('category')
        
        # --- Catch the End Date ---
        end_date_str = request.POST.get('end_date')
        end_date_obj = None
        # Only convert to a date object if it's monthly AND user actually typed a date
        if is_monthly and end_date_str:
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        # -------------------------------
        
        cat_obj = None
        if category_name:
            cat_obj, created = Category.objects.get_or_create(
                user=request.user,
                category_name=category_name,
                defaults={'category_type': 'Needs'}
            )
        
        due_date_obj = datetime.strptime(due, '%Y-%m-%d').date()
        
        if due_date_obj < date.today():
            status = 'Overdue'
        else:
            status = 'Unpaid'
            
        Bill.objects.create(
            user=request.user, 
            name=name, 
            amount=amount, 
            due_date=due_date_obj, 
            status=status,
            is_monthly=is_monthly,
            category=cat_obj,
            end_date=end_date_obj # Save the end date
        )
        
    return redirect('bills')

@login_required
def update_bill(request, bill_id, new_status):
    if request.method == 'POST':
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        
        # AUTO-EXPENSE LOGIC
        if new_status == 'Paid' and bill.status != 'Paid':
            Transaction.objects.create(
                user=request.user,
                description=f"Bill Payment: {bill.name}",
                amount=bill.amount,
                type='EXPENSE',
                category=bill.category,
                transaction_date=date.today()
            )

        # MONTHLY ROLLOVER LOGIC
        if new_status == 'Paid' and bill.is_monthly:
            bill.status = 'Paid'
            bill.save()
            
            next_due_date = add_one_month(bill.due_date)
            
            # --- THE END DATE KILL-SWITCH ---
            # If this bill has an end date, AND the next due date is past it, DO NOT CLONE
            if bill.end_date and next_due_date > bill.end_date:
                pass # Do nothing! The recurring cycle is officially finished.
            else:
                # Otherwise, it's safe to clone the next month
                if next_due_date < date.today():
                    next_status = 'Overdue'
                else:
                    next_status = 'Unpaid'
                    
                Bill.objects.create(
                    user=bill.user,
                    name=bill.name,
                    amount=bill.amount,
                    due_date=next_due_date,
                    status=next_status,
                    is_monthly=True,
                    category=bill.category,
                    end_date=bill.end_date # Carry over the same end date to the new bill
                )
            # -------------------------------------
            
        else:
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
    
    return render(request, 'transactions/edit_bill.html', {'bill': bill})


# ==========================================
# TRANSACTIONS VIEWS
# ==========================================

@login_required
def transaction_list(request):
    # 1. Grab ONLY the transactions belonging to the logged-in user
    user_txns = Transaction.objects.filter(user=request.user)

    # 2. Fetch the latest transactions for the history list
    transactions = user_txns.order_by('-transaction_date')

    # 3. Calculate totals using only that user's data
    total_income = user_txns.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = user_txns.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0

    # 4. Calculate Net
    net = total_income - total_expense

    # 5. Send it all to HTML
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
        category_name = request.POST.get('category')
        
        # --- NEW: FOREIGN KEY LOOKUP ---
        cat_obj = None
        if txn_type == 'EXPENSE' and category_name:
            cat_obj, created = Category.objects.get_or_create(
                user=request.user,
                category_name=category_name,
                defaults={'category_type': 'Needs'} # Defaulting to 'Needs' for now
            )
        # -------------------------------
        
        Transaction.objects.create(
            user=request.user,
            description=desc,
            amount=amount,
            type=txn_type,
            category=cat_obj,
            transaction_date=date.today()
        )
    return redirect('transaction_list')


@login_required
def delete_transaction(request, transaction_id):
    if request.method == 'POST':
        # Safely finds the transaction and ensures it belongs to the user before deleting
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
    
    base_query = Transaction.objects.filter(user=request.user, type='EXPENSE')
    if selected_month != 'all':
        base_query = base_query.filter(transaction_date__month=int(selected_month) + 1)

    # 1. SPECIFIC FILTERS: Pull directly from the database
    spent_data = {
        'Food': base_query.filter(category__category_name='Food').aggregate(total=Sum('amount'))['total'] or 0,
        'Transport': base_query.filter(category__category_name='Transport').aggregate(total=Sum('amount'))['total'] or 0,
        'Health': base_query.filter(category__category_name='Health').aggregate(total=Sum('amount'))['total'] or 0,
        'Utilities': base_query.filter(category__category_name='Utilities').aggregate(total=Sum('amount'))['total'] or 0,
        'Shopping': base_query.filter(category__category_name='Shopping').aggregate(total=Sum('amount'))['total'] or 0,
        'Miscellaneous': base_query.filter(category__category_name='Miscellaneous').aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # 2. BULLETPROOF FALLBACK: Query for any transaction that has NO category assigned
    uncategorized_spent = base_query.filter(category__isnull=True).aggregate(total=Sum('amount'))['total'] or 0
    
    # 3. Add those orphans into the Miscellaneous bucket
    spent_data['Miscellaneous'] += uncategorized_spent 

    categories_info = []
    g_count = w_count = b_count = 0

    for cat_name in ['Food', 'Transport', 'Utilities', 'Shopping', 'Health', 'Miscellaneous']:
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

        # ==========================================
        # SMART SUGGESTION LOGIC
        # ==========================================
        if percent < 50:
            suggestion = "Great control! Keep it up."
        elif percent < 85:
            if cat_name == "Food": suggestion = "Getting high. Try cooking at home."
            elif cat_name == "Transport": suggestion = "Consider carpooling or public transit."
            elif cat_name == "Utilities": suggestion = "Watch your AC/Electricity usage."
            elif cat_name == "Shopping": suggestion = "Hold off on impulse buying."
            elif cat_name == "Health": suggestion = "Monitor pharmacy expenses."
            elif cat_name == "Miscellaneous": suggestion = "Watch out for hidden costs."
            else: suggestion = "Monitor spending closely."
        else:
            # CRITICAL WARNING: Find the single most expensive transaction in this category
            if cat_name == 'Miscellaneous':
                # Catch both explicit "Miscellaneous" and uncategorized items
                category_txns = base_query.filter(Q(category__category_name=cat_name) | Q(category__isnull=True))
            else:
                category_txns = base_query.filter(category__category_name=cat_name)
                
            top_expense = category_txns.order_by('-amount').first()
            
            if top_expense:
                suggestion = f"⚠️ Cut back on: '{top_expense.description}' (₱{top_expense.amount})"
            else:
                suggestion = "⚠️ Critical: Stop spending in this category!"
        # ==========================================

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