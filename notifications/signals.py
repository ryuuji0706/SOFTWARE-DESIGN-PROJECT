from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Bill
from .models import Reminder

@receiver(post_save, sender=Bill)
def create_reminder(sender, instance, created, **kwargs):
    """
    Fires every time a Bill is saved. 
    If created: makes a new reminder.
    If updated to Paid: marks the reminder as Completed!
    """
    if created:
        reminder_date = getattr(instance, 'reminder_date', instance.due_date)
        Reminder.objects.create(
            user=instance.user,
            name=f"Pay {instance.name}",
            amount=instance.amount,
            status='Unpaid',
        )
    else:
        # If the bill was just updated to 'Paid'
        if instance.status == 'Paid':
            # Find the oldest Unpaid reminder with this exact name
            reminder = Reminder.objects.filter(
                user=instance.user,
                name=f"Pay {instance.name}",
                status='Unpaid'
            ).first()
            
            # If we found it, mark it as Completed!
            if reminder:
                reminder.status = 'Completed'
                reminder.save()
        
# --- ADD THIS NEW CLEANUP SIGNAL ---
@receiver(post_delete, sender=Bill)
def delete_linked_reminder(sender, instance, **kwargs):
    """
    Fires every time a Bill is deleted.
    Hunts down the matching reminder and deletes it too!
    """
    Reminder.objects.filter(
        user=instance.user, 
        name=f"Pay {instance.name}"
    ).delete()