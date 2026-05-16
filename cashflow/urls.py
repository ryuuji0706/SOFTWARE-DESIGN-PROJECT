"""
URL configuration for cashflow project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# Import views from all your apps with aliases to avoid naming conflicts
from analytics import views as analytics_views
from users import views as users_views
from transactions import views as transactions_views
from notifications import views as notifications_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Analytics (Main Dashboard)
    path('', analytics_views.dashboard, name='dashboard'),
    
    # Users (Authentication)
    path('login/', users_views.login_user, name='login'),
    path('register/', users_views.register_user, name='register'),
    path('logout/', users_views.logout_user, name='logout'),
    
    # Transactions (Income & Expenses)
    path('transactions/', transactions_views.transaction_list, name='transaction_list'),
    path('transactions/add/', transactions_views.add_transaction, name='add_transaction'),
    path('transactions/delete/<int:transaction_id>/', transactions_views.delete_transaction, name='delete_transaction'),
    
    # Budgets (Spending Limits)
    path('budget/', transactions_views.budget_view, name='budget'),
    path('budget/set/', transactions_views.set_budget, name='set_budget'),
    
    # Notifications (Alerts & Reminders)
    path('reminders/', notifications_views.reminders_view, name='reminders'),
    
    # NavBar Links (Additional Pages)
    path('bills/', transactions_views.bills_view, name='bills'),
    path('bills/add/', transactions_views.add_bill, name='add_bill'),
    path('bills/update/<int:bill_id>/<str:new_status>/', transactions_views.update_bill, name='update_bill'),
    path('bills/delete/<int:bill_id>/', transactions_views.delete_bill, name='delete_bill'),
    path('bills/edit/<int:bill_id>/', transactions_views.edit_bill, name='edit_bill'),
    
    path('expenses/', transactions_views.expenses_view, name='expenses'),
    path('summary/', analytics_views.summary_view, name='summary'),
    path('suggestions/', analytics_views.suggestions_view, name='suggestions'),
    
    
]