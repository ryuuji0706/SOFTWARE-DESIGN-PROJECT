from django.shortcuts import render

def dashboard(request):
    # Eventually, we will add math here to calculate the 50/30/20 splits
    # For now, we use dummy data. Later, these will come from your Database!
    budget = 5000
    spent = 2000
    
    # Calculate values in Python
    remaining = budget - spent
    # Avoid division by zero if budget is 0
    percentage = (spent / budget) * 100 if budget > 0 else 0

    context = {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'percentage': percentage,
    }
    
    # FIX: Pass the 'context' dictionary into the render function!
    return render(request, 'analytics/dashboard.html', context)

# --- NEW PLACEHOLDER VIEWS ---

def summary_view(request):
    # Placeholder for the summary page
    return render(request, 'analytics/summary.html')

def suggestions_view(request):
    # Placeholder for the suggestions/tips page
    return render(request, 'analytics/suggestion.html')