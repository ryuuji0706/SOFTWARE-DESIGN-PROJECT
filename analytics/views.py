from django.shortcuts import render

# Create your views here.
def dashboard(request):
    # Eventually, we will add math here to calculate the 50/30/20 splits
    return render(request, 'analytics/dashboard.html')