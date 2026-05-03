from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    # Links to the built-in Django User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20) # e.g., 'Needs', 'Wants', 'Savings'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category_name} ({self.category_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - ₱{self.amount} on {self.transaction_date}"