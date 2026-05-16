from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# When someone goes to your main website URL, immediately send them to the Dashboard
@login_required
def index(request):
    return redirect('dashboard')