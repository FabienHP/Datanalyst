from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
from django.db import connections, models, DEFAULT_DB_ALIAS
from faker import Faker
import random
import uuid

class Command(BaseCommand):
    help = 'Populate the test_db database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating test_db with users, gifts, and events...")

        fake = Faker()
        devices = ['mobile', 'pc', 'tablet']
        os_choices = ['Windows', 'macOS', 'Linux']
        browsers = ['Chrome', 'Firefox', 'Safari']

        events = [
            ('HOME', 'Arrival on the home page'),
            ('GAME', 'Access to the game page'),
            ('END', 'Arrival on the end page'),
            ('RESU', 'Display of results')
        ]

        # Define models inside the command
        class User(models.Model):
            firstname = models.CharField(max_length=255, null=True, blank=True)
            lastname = models.CharField(max_length=255, null=True, blank=True)
            email = models.EmailField(null=True, blank=True)
            rule_at = models.DateTimeField(null=True, blank=True)
            send_email_at = models.DateTimeField(null=True, blank=True)
            played_at = models.DateTimeField(null=True, blank=True)
            target_id = models.CharField(max_length=10, null=True, blank=True)
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

        # Insert data into tables
        with connections['test_db'].cursor() as cursor:
            for event_code, event_description in events:
                cursor.execute(
                    "INSERT INTO events (code, description, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                    [event_code, event_description, timezone.now(), timezone.now()]
                )

            # Create users
            for i in range(500):
                user_data = {
                    'firstname': fake.first_name(),
                    'lastname': fake.last_name(),
                    'email': fake.email(),
                    'rule_at': fake.date_time_this_year(),
                    'send_email_at': fake.date_time_this_year(),
                    'played_at': fake.date_time_this_year(),
                    'target_id': fake.lexify(text='??????????'),
                    'end_at': fake.date_time_this_year(),
                    'optin_at': fake.date_time_this_year(),
                    'src': fake.lexify(text='???'),
                    'ip': fake.ipv4(),
                    'os': random.choice(os_choices),
                    'device': random.choice(devices),
                    'browser': random.choice(browsers),
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
                cursor.execute(
                    """
                    INSERT INTO users (firstname, lastname, email, rule_at, send_email_at, played_at, target_id, end_at, optin_at, src, ip, os, device, browser, created_at, updated_at)
                    VALUES (%(firstname)s, %(lastname)s, %(email)s, %(rule_at)s, %(send_email_at)s, %(played_at)s, %(target_id)s, %(end_at)s, %(optin_at)s, %(src)s, %(ip)s, %(os)s, %(device)s, %(browser)s, %(created_at)s, %(updated_at)s)
                    """,
                    user_data
                )
                user_id = cursor.lastrowid

                # Assign some users to events
                if i < 400:
                    num_events = random.randint(1, 4)
                    selected_events = random.sample(events, num_events)
                    for event_code, _ in selected_events:
                        cursor.execute(
                            "INSERT INTO event_user (user_id, event_id, created_at, updated_at) VALUES (%s, (SELECT id FROM events WHERE code = %s), %s, %s)",
                            [user_id, event_code, timezone.now(), timezone.now()]
                        )

            # Create gifts
            for i in range(50):
                gift_data = {
                    'code': fake.lexify(text='??????'),
                    'type': random.choice(['Type1', 'Type2']),
                    'segment': random.randint(1, 10),
                    'date_to_win': fake.date_time_this_year(),
                    'image': fake.image_url(),
                    'mention': fake.text(),
                    'description': fake.sentence(),
                    'subtitle': fake.sentence(),
                    'user_id': random.choice([None] + list(range(1, 501))) if i < 25 else None,
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
                cursor.execute(
                    """
                    INSERT INTO gifts (code, type, segment, date_to_win, image, mention, description, subtitle, user_id, created_at, updated_at)
                    VALUES (%(code)s, %(type)s, %(segment)s, %(date_to_win)s, %(image)s, %(mention)s, %(description)s, %(subtitle)s, %(user_id)s, %(created_at)s, %(updated_at)s)
                    """,
                    gift_data
                )

        self.stdout.write(self.style.SUCCESS('Test database populated successfully!'))
