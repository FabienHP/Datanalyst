from django.core.management.base import BaseCommand
from django.db import connections, models, DEFAULT_DB_ALIAS
from django.db.utils import OperationalError
import uuid

class Command(BaseCommand):
    help = 'Create tables in test_db similar to Laravel schema and insert test data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating tables in test_db...")

        # Define models
        class User(models.Model):
            firstname = models.CharField(max_length=255, null=True, blank=True)
            lastname = models.CharField(max_length=255, null=True, blank=True)
            email = models.EmailField(null=True, blank=True)
            rule_at = models.DateTimeField(null=True, blank=True)
            send_email_at = models.DateTimeField(null=True, blank=True)
            played_at = models.DateTimeField(null=True, blank=True)
            target_id = models.CharField(max_length=10, null=True, blank=True)
            step = models.CharField(max_length=255, db_index=True)
            end_at = models.DateTimeField(null=True, blank=True)
            optin_at = models.DateTimeField(null=True, blank=True)
            src = models.CharField(max_length=3, null=True, blank=True)
            ip = models.GenericIPAddressField(null=True, blank=True)
            os = models.CharField(max_length=50, null=True, blank=True)
            device = models.CharField(max_length=50, null=True, blank=True)
            browser = models.CharField(max_length=50, null=True, blank=True)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            class Meta:
                app_label = 'your_app'
                db_table = 'users'

        class Gift(models.Model):
            code = models.CharField(max_length=255)
            type = models.CharField(max_length=255)
            segment = models.IntegerField(null=True, blank=True)
            date_to_win = models.DateTimeField()
            image = models.CharField(max_length=255, null=True, blank=True)
            mention = models.TextField(null=True, blank=True)
            mention_2 = models.TextField(null=True, blank=True)
            description = models.CharField(max_length=255, null=True, blank=True)
            subtitle = models.CharField(max_length=255, null=True, blank=True)
            user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            class Meta:
                app_label = 'your_app'
                db_table = 'gifts'

        class Event(models.Model):
            code = models.CharField(max_length=5, db_index=True)
            description = models.CharField(max_length=255)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            class Meta:
                app_label = 'your_app'
                db_table = 'events'

        class EventUser(models.Model):
            user = models.ForeignKey(User, on_delete=models.CASCADE)
            event = models.ForeignKey(Event, on_delete=models.CASCADE)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            class Meta:
                app_label = 'your_app'
                db_table = 'event_user'

        # Create tables
        with connections['test_db'].schema_editor() as schema_editor:
            schema_editor.create_model(User)
            schema_editor.create_model(Gift)
            schema_editor.create_model(Event)
            schema_editor.create_model(EventUser)

        self.stdout.write(self.style.SUCCESS('Tables created successfully in test_db!'))
