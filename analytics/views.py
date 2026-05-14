from django.shortcuts import render
from django.db.models import Sum, Q
from transactions.models import Transaction, Bill
from notifications.models import Reminder

def dashboard(request):
    # --- WORKING BACKEND FEATURES (BILLS) ---
    all_bills = Bill.objects.all()
    
    # Fetch the reminders (filtering by 'Unpaid' so only pending ones show up)
    unpaid_reminders = Reminder.objects.filter(status='Unpaid').order_by('-created_at')
    
    total_bills = all_bills.count()
    paid_bills = all_bills.filter(status='Paid').count()
    unpaid_bills = all_bills.filter(status='Unpaid').count()
    recent_bills = all_bills.order_by('-due_date')[:5]

    # --- NON-FUNCTIONING FEATURES (REMINDERS) ---
    # We pass these as empty/dummy variables to keep your HTML structure intact
    reminder_count = 0
    recent_reminders = []

    context = {
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'recent_bills': recent_bills,
        
        # Modal Lists
        'all_bills_list': all_bills,
        'paid_bills_list': all_bills.filter(status='Paid'),
        'unpaid_bills_list': all_bills.filter(status='Unpaid'),
        
        # Reminders Data
        'reminder_count': unpaid_reminders.count(),
        'recent_reminders': unpaid_reminders[:5], # Only send the 5 most recent to the dashboard UI
        
        # Kept for the non-functioning UI
        'reminder_count': reminder_count,
        'recent_reminders': recent_reminders, 
    }
    
    return render(request, 'analytics/dashboard.html', context)

def summary_view(request):
    # 1. Totals
    income = Transaction.objects.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
    expense = Transaction.objects.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
    
    savings = income - expense
    rate = round((savings / income) * 100, 1) if income > 0 else 0

    # 2. Categorization (Replicating your JS keyword logic using Django Q objects)
    food = Transaction.objects.filter(type='EXPENSE').filter(Q(description__icontains='food') | Q(description__icontains='meal')).aggregate(total=Sum('amount'))['total'] or 0
    transport = Transaction.objects.filter(type='EXPENSE').filter(Q(description__icontains='transport') | Q(description__icontains='gas')).aggregate(total=Sum('amount'))['total'] or 0
    health = Transaction.objects.filter(type='EXPENSE').filter(description__icontains='health').aggregate(total=Sum('amount'))['total'] or 0
    utilities = Transaction.objects.filter(type='EXPENSE').filter(Q(description__icontains='electric') | Q(description__icontains='water') | Q(description__icontains='internet') | Q(description__icontains='utility')).aggregate(total=Sum('amount'))['total'] or 0
    
    # In your JS, anything else falls back to 'Shopping'
    shopping = expense - (food + transport + health + utilities)
    if shopping < 0: 
        shopping = 0

    # 3. Find max for the progress bars
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
    return render(request, 'analytics/analytics.html', context)

# --- PLACEHOLDER VIEWS ---

def suggestions_view(request):
    return render(request, 'analytics/suggestion.html')