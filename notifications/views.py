from django.shortcuts import render
from .models import Reminder
from transactions.models import Bill

def reminders_view(request):
    # Fetch Overdue Bills from the Transactions app
    overdue_bills = Bill.objects.filter(status='Overdue').order_by('-due_date')
    
    # Fetch Manual Reminders
    all_reminders = Reminder.objects.all().order_by('-created_at')
    
    context = {
        'reminders': all_reminders,
        'overdue_bills': overdue_bills,
        
        # Calculate the stats for the top cards
        'pending': all_reminders.filter(status='Pending').count(),
        'done': all_reminders.filter(status='Completed').count(),
        'overdue': overdue_bills.count(),
    }
    
    return render(request, 'notifications/reminders.html', context)