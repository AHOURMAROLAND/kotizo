from celery import shared_task
from core.logger import logger


@shared_task
def supprimer_anciennes_conversations():
    from django.utils import timezone
    from datetime import timedelta
    from .models import ConversationIA

    limite = timezone.now() - timedelta(days=90)
    count, _ = ConversationIA.objects.filter(date_derniere_activite__lt=limite).delete()
    if count:
        logger.info(f'{count} conversations IA supprimees')