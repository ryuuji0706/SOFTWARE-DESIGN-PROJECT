from django.shortcuts import render
from django.db.models import Sum, Q
from transactions.models import Transaction, Bill
from notifications.models import Reminder
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    all_bills = Bill.objects.filter(user=request.user)
    unpaid_reminders = Reminder.objects.filter(user=request.user, status='Unpaid').order_by('-created_at')
    
    context = {
        'total_bills': all_bills.count(),
        'paid_bills': all_bills.filter(status='Paid').count(),
        'unpaid_bills': all_bills.filter(status='Unpaid').count(),
        
        # 1. NEW: Add Overdue Count
        'overdue_bills': all_bills.filter(status='Overdue').count(), 
        
        'recent_bills': all_bills.order_by('-due_date')[:5],
        
        'all_bills_list': all_bills,
        'paid_bills_list': all_bills.filter(status='Paid'),
        'unpaid_bills_list': all_bills.filter(status='Unpaid'),
        
        # 2. NEW: Add Overdue List for the Modal
        'overdue_bills_list': all_bills.filter(status='Overdue'), 
        
        'reminder_count': unpaid_reminders.count(),
        'recent_reminders': unpaid_reminders[:5], 
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def summary_view(request):
    # 1. Get Income and Expense
    income = Transaction.objects.filter(user=request.user, type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    expense = Transaction.objects.filter(user=request.user, type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    
    # 2. Calculate Savings and Savings Rate
    savings = income - expense
    rate = 0
    if income > 0:
        rate = round((savings / income) * 100)
    if rate < 0:
        rate = 0 # Don't show a negative savings rate

    # 3. Fetch Category Breakdowns using the double-underscore trick!
    base_expense = Transaction.objects.filter(user=request.user, type='EXPENSE')
    
    food = base_expense.filter(category__category_name='Food').aggregate(total=Sum('amount'))['total'] or 0
    transport = base_expense.filter(category__category_name='Transport').aggregate(total=Sum('amount'))['total'] or 0
    shopping = base_expense.filter(category__category_name='Shopping').aggregate(total=Sum('amount'))['total'] or 0
    health = base_expense.filter(category__category_name='Health').aggregate(total=Sum('amount'))['total'] or 0
    utilities = base_expense.filter(category__category_name='Utilities').aggregate(total=Sum('amount'))['total'] or 0
    miscellaneous = base_expense.filter(category__category_name='Miscellaneous').aggregate(total=Sum('amount'))['total'] or 0

    # 4. Find the highest category to scale the progress bars correctly (max_cat)
    cat_values = [food, transport, shopping, health, utilities, miscellaneous]
    max_cat = max(cat_values) if max(cat_values) > 0 else 1 # Fallback to 1 to prevent divide-by-zero errors in HTML

    context = {
        'income': income,
        'expense': expense,
        'savings': savings,
        'rate': rate,
        
        'food': food,
        'transport': transport,
        'shopping': shopping,
        'health': health,
        'utilities': utilities,
        'miscellaneous': miscellaneous,
        'max_cat': max_cat, # CRITICAL for the progress bars!
    }
    
    return render(request, 'analytics/analytics.html', context)

# --- PLACEHOLDER VIEWS ---

@login_required
def suggestions_view(request):
    return render(request, 'analytics/suggestion.html')