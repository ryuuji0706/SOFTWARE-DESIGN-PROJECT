from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    name = 'notifications'
    
class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    # --- ADD THIS FUNCTION ---
    def ready(self):
        # This tells Django to load your signals when the app starts!
        import notifications.signals
