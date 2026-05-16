from django.shortcuts import render
from .models import Reminder
from transactions.models import Bill
from django.contrib.auth.decorators import login_required

@login_required
def reminders_view(request):
    # Fetch Overdue Bills for the logged-in user only
    overdue_bills = Bill.objects.filter(user=request.user, status='Overdue').order_by('-due_date')
    
    # Fetch Unpaid Bills for the logged-in user only
    unpaid_bills_count = Bill.objects.filter(user=request.user, status='Unpaid').count()
    
    # Fetch Manual Reminders for the logged-in user only
    all_reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reminders': all_reminders,
        'overdue_bills': overdue_bills,
        'pending': unpaid_bills_count,
        # Calculate the stats for the top cards
        'done': all_reminders.filter(status='Completed').count(),
        'overdue': overdue_bills.count(),
    }
    
    return render(request, 'notifications/reminders.html', context)