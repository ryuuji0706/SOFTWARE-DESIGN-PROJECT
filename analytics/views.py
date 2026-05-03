from django.shortcuts import render
from django.db.models import Sum
from transactions.models import Transaction

def dashboard(request):
    # 1. Fetch Total Income (This acts as your Total Budget)
    # The 'or 0' ensures that if there are no income records yet, it defaults to 0 instead of 'None'
    income_query = Transaction.objects.filter(type='INCOME').aggregate(total=Sum('amount'))
    budget = income_query['total'] or 0 
    
    # 2. Fetch Total Expenses (Total Spent)
    expense_query = Transaction.objects.filter(type='EXPENSE').aggregate(total=Sum('amount'))
    spent = expense_query['total'] or 0 
    
    # 3. Calculate Remaining and Percentage
    remaining = budget - spent
    percentage = (spent / budget) * 100 if budget > 0 else 0

    # 4. (Optional but recommended) Fetch 50/30/20 breakdowns for later use
    # needs_spent = Transaction.objects.filter(type='EXPENSE', category__category_type='Needs').aggregate(total=Sum('amount'))['total'] or 0
    # wants_spent = Transaction.objects.filter(type='EXPENSE', category__category_type='Wants').aggregate(total=Sum('amount'))['total'] or 0
    # savings_spent = Transaction.objects.filter(type='EXPENSE', category__category_type='Savings').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'percentage': round(percentage, 1), # Rounded for a cleaner UI on the chart
    }
    
    return render(request, 'analytics/dashboard.html', context)

# --- PLACEHOLDER VIEWS ---

def summary_view(request):
    return render(request, 'analytics/summary.html')

def suggestions_view(request):
    return render(request, 'analytics/suggestion.html')