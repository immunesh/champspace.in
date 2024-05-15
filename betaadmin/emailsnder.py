from django.core.mail import send_mail
from django.conf import settings
def send_forgot_mail(to,token):
    subject = 'Forgot Password'
    message = f'To Change your password please click the link below http://127.0.0.1:8000/beta/forgot-password/{token}'

    email_from = 'noreply@gmail.com'
    recipient_list = [to]

    send_mail(subject, message, email_from, recipient_list)
    return True