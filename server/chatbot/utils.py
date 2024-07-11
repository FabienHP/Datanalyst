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


def calculate_md5(file):
    hash_md5 = hashlib.md5()
    for chunk in file.chunks():
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

def filter_complex_metadata(metadata):
    """
    Filtrer les métadonnées pour ne conserver que les types simples.

    Args:
        metadata (dict): Les métadonnées à filtrer.

    Returns:
        dict: Les métadonnées filtrées.
    """
    simple_types = (str, int, float, bool)
    filtered_metadata = {k: v for k, v in metadata.items() if isinstance(v, simple_types)}
    return filtered_metadata