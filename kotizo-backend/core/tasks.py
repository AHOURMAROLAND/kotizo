from celery import shared_task
from core.logger import KotizoLogger

logger = KotizoLogger('core.tasks')


@shared_task
def test_celery():
    logger.info('test_celery', {'message': 'Celery fonctionne correctement'})
    return 'OK'
