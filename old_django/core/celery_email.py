from django.core import mail
from django.core.mail import EmailMessage


class Mailer:
    def __init__(self, from_email=None):
        self.connection = mail.get_connection()
        self.from_email = from_email

    def send_messages(self, subject, content, to_emails):
        messages = self.__generate_messages(subject, content, to_emails)
        self.__send_mail(messages)

    def __send_mail(self, mail_messages):
        self.connection.open()
        self.connection.send_messages(mail_messages)
        self.connection.close()

    def __generate_messages(self, subject, content, to_emails):
        messages = []
        for recipient in to_emails:
            message_content = 'Code: {}'.format(content)
            message = EmailMessage(subject, message_content, to=[recipient], from_email=self.from_email)
            messages.append(message)
        return messages
