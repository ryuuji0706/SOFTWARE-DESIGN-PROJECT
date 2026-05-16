from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Bill
from .models import Reminder

@receiver(post_save, sender=Bill)
def create_reminder(sender, instance, created, **kwargs):
    """
    Fires every time a Bill is saved. 
    Creates the linked Reminder record automatically.
    """
    # If the bill was just created (not just updated)
    if created:
        # We use the bill's due_date as the reminder_date 
        reminder_date = getattr(instance, 'reminder_date', instance.due_date)
        
        Reminder.objects.create(
            user=instance.user,
            # If your Reminder model has a ForeignKey to Bill, uncomment the next line:
            # bill=instance, 
            name=f"Pay {instance.name}",
            amount=instance.amount,
            status='Unpaid', # This matches the filter in your Dashboard!
            # remind_on=reminder_date  <-- Use this if your model has a remind_on/reminder_date field
        )
        
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