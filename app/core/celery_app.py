# Emprestimo-Facil\app\core\celery_app.py

from celery import Celery
from app.core.config import settings

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