from django.shortcuts import render, redirect

# Dashboard
def index(request):
    return redirect('dashboard')

def dashboard(request):
    # Initialize session
    if 'budget' not in request.session:
        request.session['budget'] = 0
    if 'spent' not in request.session:
        request.session['spent'] = 0

    if request.method == "POST":
        try:
            request.session['budget'] = float(request.POST.get('budget', request.session['budget']))
            request.session['spent'] = float(request.POST.get('spent', request.session['spent']))
        except ValueError:
            pass

    context = {
        'budget': request.session['budget'],
        'spent': request.session['spent']
    }

    return render(request, 'cashflow/dashboard.html', context)


def expenses(request):
    return render(request, 'cashflow/expenses.html')


def bills(request):
    return render(request, 'cashflow/bills.html')


def summary(request):
    return render(request, 'cashflow/summary.html')


def suggestion(request):
    return render(request, 'cashflow/suggestion.html')


def add_bill(request):
    if request.method == "POST":
        name = request.POST.get("bill_name")
        amount = float(request.POST.get("amount"))
        due_date = request.POST.get("due_date")

        if 'bills' not in request.session:
            request.session['bills'] = []

        bills = request.session['bills']

        bills.append({
            "name": name,
            "amount": amount,
            "due_date": due_date
        })

        request.session['bills'] = bills

        if 'spent' not in request.session:
            request.session['spent'] = 0

        request.session['spent'] += amount

    return redirect('bills')
