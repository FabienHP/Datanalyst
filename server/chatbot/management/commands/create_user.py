from django.core.management.base import BaseCommand
from chatbot.models import CustomUser

class Command(BaseCommand):
    help = 'Create a new custom user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user')
        parser.add_argument('email', type=str, help='The email of the user')
        parser.add_argument('password', type=str, help='The password of the user')
        parser.add_argument('--first_name', type=str, help='The first name of the user', default='')
        parser.add_argument('--last_name', type=str, help='The last name of the user', default='')
        parser.add_argument('--role', type=str, choices=['user', 'admin'], help='The role of the user', default='user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        role = kwargs['role']

        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists.'))
        else:
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            self.stdout.write(self.style.SUCCESS(f'User "{username}" created successfully.'))
