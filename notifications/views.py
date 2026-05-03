from django.shortcuts import render

def view_alerts(request):
    # Logic to trigger reminders based on bill due dates
    return render(request, 'notifications/alerts.html')