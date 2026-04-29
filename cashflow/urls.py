from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses/', views.expenses, name='expenses'),
    path('bills/', views.bills, name='bills'),
    path('summary/', views.summary, name='summary'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('add_bill/', views.add_bill, name='add_bill'),
]
