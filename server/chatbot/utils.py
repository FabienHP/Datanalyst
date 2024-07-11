from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import hashlib

def send_password_reset_email(user, reset_url):
    subject = 'Set your password'
    html_content = render_to_string('set_password_email_new_user.html', {'reset_url': reset_url})
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()