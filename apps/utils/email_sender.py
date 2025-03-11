import logging

from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives


class SendEmail:
    @staticmethod
    def send_email(subject, body, to, **kwargs):
        try:
            msg = EmailMultiAlternatives(subject=subject, body=body, to=to, **kwargs)
            msg.attach_alternative(body, "text/html")
            return msg.send()

        except Exception as e:
            logging.error(f"There was an error sending an email. \n{e}")