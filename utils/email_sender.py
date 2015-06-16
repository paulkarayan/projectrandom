# Email utilities

import os
import ConfigParser
import logging
import smtplib
from email.Utils import COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONFIG_FILE = ''

class EmailSender:
    def __init__(self, config_file=CONFIG_FILE):
        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser(config_file))
        self.smtp_server = config.get("Email", "server")
        self.smtp_port = config.getint("Email", "port")
        self.use_tls = config.getboolean("Email", "use_tls")
        self.email_username = config.get("Email", "username")
        self.email_password = config.get("Email", "password")

    # to_address, cc, & bcc should be comma-separated strings
    def send_email(self, to_address, subject, content, content_type='html', cc='', bcc=''):
        try:
            server = smtplib.SMTP(self.smtp_server + ":" + str(self.smtp_port))
            if self.use_tls:
                server.starttls()
            server.login(self.email_username, self.email_password)

            message = MIMEMultipart()
            message['Subject'] = subject
            message['From'] = self.email_username
            message['To'] = COMMASPACE.join(to_address.split(","))
            message['cc'] = cc
            message['bcc'] = bcc
            if content_type == 'html':
                message.attach(MIMEText(content, 'html'))
            if content_type == 'text':
                message.attach(MIMEText(content, 'plain'))
            server.sendmail(self.email_username, EmailSender.build_recipient_list(to_address, cc, bcc),
                            message.as_string())
            server.quit()
        except smtplib.SMTPException, e:
            logging.error("SMTP Connection failed with an exception: " + e.message)

    @staticmethod
    def build_recipient_list(to_address, cc, bcc):
        recipients = to_address.split(",")
        if cc:
            recipients.append(cc.split(","))
        if bcc:
            recipients.append(bcc.split(","))
        return recipients
