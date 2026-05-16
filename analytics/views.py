from django.shortcuts import render
from django.db.models import Sum, Q
from transactions.models import Transaction, Bill
from notifications.models import Reminder
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # 1. Grab Bills belonging ONLY to the logged-in user
    all_bills = Bill.objects.filter(user=request.user)
    
    # 2. Grab Reminders belonging ONLY to the logged-in user
    unpaid_reminders = Reminder.objects.filter(user=request.user, status='Unpaid').order_by('-created_at')
    
    context = {
        'total_bills': all_bills.count(),
        'paid_bills': all_bills.filter(status='Paid').count(),
        'unpaid_bills': all_bills.filter(status='Unpaid').count(),
        'recent_bills': all_bills.order_by('-due_date')[:5],
        
        # Modal Lists
        'all_bills_list': all_bills,
        'paid_bills_list': all_bills.filter(status='Paid'),
        'unpaid_bills_list': all_bills.filter(status='Unpaid'),
        
        # Reminders Data
        'reminder_count': unpaid_reminders.count(),
        'recent_reminders': unpaid_reminders[:5], 
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def summary_view(request):
    # 1. Grab ONLY the transactions belonging to the logged-in user
    user_txns = Transaction.objects.filter(user=request.user)

    # 2. Calculate Totals from that specific user's data
    income = user_txns.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    expense = user_txns.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    
    savings = income - expense
    rate = round((savings / income) * 100, 1) if income > 0 else 0

    # 3. Categorization (Using the user's expenses only)
    user_expenses = user_txns.filter(type='EXPENSE')
    
    food = user_expenses.filter(Q(description__icontains='food') | Q(description__icontains='meal')).aggregate(total=Sum('amount'))['total'] or 0
    transport = user_expenses.filter(Q(description__icontains='transport') | Q(description__icontains='gas')).aggregate(total=Sum('amount'))['total'] or 0
    health = user_expenses.filter(description__icontains='health').aggregate(total=Sum('amount'))['total'] or 0
    utilities = user_expenses.filter(Q(description__icontains='electric') | Q(description__icontains='water') | Q(description__icontains='internet') | Q(description__icontains='utility')).aggregate(total=Sum('amount'))['total'] or 0
    
    # Shopping is the fallback
    shopping = expense - (food + transport + health + utilities)
    if shopping < 0: 
        shopping = 0

    # 4. Find max for the progress bars
    max_cat = max([food, transport, shopping, health, utilities, 1])

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
        'max_cat': max_cat
    }
    
    # Make sure 'analytics/analytics.html' matches your actual file name!
    return render(request, 'analytics/analytics.html', context)

# --- PLACEHOLDER VIEWS ---

@login_required
def suggestions_view(request):
    return render(request, 'analytics/suggestion.html')