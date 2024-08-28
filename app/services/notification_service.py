# Emprestimo-Facil\app\services\notification_service.py

from abc import ABC, abstractmethod
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging

logger = logging.getLogger(__name__)

class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, to: str, message: str) -> bool:
        pass

class EmailNotificationService(NotificationService):
    def __init__(self):
        self.smtp_settings = settings.get_email_settings()

    def send_notification(self, to: str, message: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_settings['emails_from_email']
            msg['To'] = to
            msg['Subject'] = "Notificação do Empréstimo Fácil"
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_settings['smtp_host'], self.smtp_settings['smtp_port'])
            server.starttls()
            server.login(self.smtp_settings['smtp_user'], self.smtp_settings['smtp_password'])
            server.send_message(msg)
            server.quit()
            logger.info(f"E-mail enviado com sucesso para {to}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {to}: {str(e)}")
            return False

class SMSNotificationService(NotificationService):
    def __init__(self):
        self.api_key = settings.sms_api_key
        self.sender_id = settings.sms_sender_id

    def send_notification(self, to: str, message: str) -> bool:
        if not self.api_key or not self.sender_id:
            logger.error("SMS API key or sender ID not configured")
            return False
        
        try:
            # Exemplo usando a API do Twilio
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.api_key}/Messages.json"
            payload = {
                "Body": message,
                "From": self.sender_id,
                "To": to
            }
            response = requests.post(url, data=payload, auth=(self.api_key, settings.sms_auth_token))
            if response.status_code == 201:
                logger.info(f"SMS enviado com sucesso para {to}")
                return True
            else:
                logger.error(f"Erro ao enviar SMS para {to}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar SMS para {to}: {str(e)}")
            return False

class WhatsAppNotificationService(NotificationService):
    def __init__(self):
        self.api_key = settings.whatsapp_api_key

    def send_notification(self, to: str, message: str) -> bool:
        if not self.api_key:
            logger.error("WhatsApp API key not configured")
            return False
        
        try:
            # Exemplo usando a API do Twilio para WhatsApp
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.api_key}/Messages.json"
            payload = {
                "Body": message,
                "From": f"whatsapp:{settings.whatsapp_from_number}",
                "To": f"whatsapp:{to}"
            }
            response = requests.post(url, data=payload, auth=(self.api_key, settings.whatsapp_auth_token))
            if response.status_code == 201:
                logger.info(f"Mensagem WhatsApp enviada com sucesso para {to}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem WhatsApp para {to}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp para {to}: {str(e)}")
            return False

class TelegramNotificationService(NotificationService):
    def __init__(self):
        self.bot_token = settings.telegram_bot_token

    def send_notification(self, to: str, message: str) -> bool:
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": to,
                "text": message
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Mensagem Telegram enviada com sucesso para {to}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem Telegram para {to}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram para {to}: {str(e)}")
            return False

class NotificationFactory:
    @staticmethod
    def get_notification_service(service_type: str) -> NotificationService:
        if service_type == "email":
            return EmailNotificationService()
        elif service_type == "sms":
            return SMSNotificationService()
        elif service_type == "whatsapp":
            return WhatsAppNotificationService()
        elif service_type == "telegram":
            return TelegramNotificationService()
        else:
            raise ValueError(f"Unsupported notification service: {service_type}")