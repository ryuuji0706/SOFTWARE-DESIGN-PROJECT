from django.shortcuts import render
from django.db.models import Sum
from django.shortcuts import render
from transactions.models import Transaction, Bill

def dashboard(request):
    # --- WORKING BACKEND FEATURES (BILLS) ---
    all_bills = Bill.objects.all()
    
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
        
        # Kept for the non-functioning UI
        'reminder_count': reminder_count,
        'recent_reminders': recent_reminders, 
    }
    
    return render(request, 'analytics/dashboard.html', context)

# --- PLACEHOLDER VIEWS ---

def summary_view(request):
    return render(request, 'analytics/summary.html')

def suggestions_view(request):
    return render(request, 'analytics/suggestion.html')