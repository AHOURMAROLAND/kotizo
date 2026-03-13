from celery import shared_task
from django.utils import timezone
from core.logger import logger


@shared_task
def expirer_cotisations():
    from .models import Cotisation
    expirees = Cotisation.objects.filter(
        statut='active',
        date_expiration__lte=timezone.now()
    )
    count = expirees.update(statut='expiree')
    if count:
        logger.info(f'{count} cotisations expirees')


@shared_task
def generer_pdf_participants(cotisation_id):
    from .models import Cotisation
    try:
        cotisation = Cotisation.objects.get(id=cotisation_id)
        logger.cotisation('Generation PDF participants', cotisation_id=str(cotisation_id))
    except Exception as e:
        logger.error(f'Erreur generation PDF : {str(e)}')