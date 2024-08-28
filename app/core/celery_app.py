# Emprestimo-Facil\app\core\celery_app.py

from celery import Celery
from app.core.config import settings
from app.services.notification_service import NotificationFactory
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "emprestimo_facil",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Exemplo de tarefa:
@celery_app.task
def exemplo_tarefa_assincrona(param1, param2):
    # Lógica da tarefa aqui
    result = param1 + param2
    return result

# Para usar:
# from app.core.celery_app import exemplo_tarefa_assincrona
# resultado = exemplo_tarefa_assincrona.delay(10, 20)

@celery_app.task
def enviar_notificacao_async(to: str, message: str, notification_type: str):
    try:
        notification_factory = NotificationFactory()
        notification_service = notification_factory.get_notification_service(notification_type)
        result = notification_service.send_notification(to, message)
        if result:
            logger.info(f"Notificação enviada com sucesso para {to}")
        else:
            logger.error(f"Falha ao enviar notificação para {to}")
        return result
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {str(e)}")
        return False