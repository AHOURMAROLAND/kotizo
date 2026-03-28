from celery import shared_task
from django.utils import timezone
from core.logger import KotizoLogger

logger = KotizoLogger('cotisations.tasks')


@shared_task
def expirer_cotisations():
    from .models import Cotisation
    maintenant = timezone.now()
    expirees = Cotisation.objects.filter(
        statut='active',
        date_expiration__lte=maintenant,
        supprime=False
    )
    nb = expirees.update(statut='expiree')
    logger.info('cotisations_expirees', {'nb': nb})


@shared_task
def envoyer_rappels():
    from .models import Cotisation
    from core.email_router import envoyer_email
    from core.whatsapp import envoyer_message

    maintenant = timezone.now()
    dans_12h = maintenant + timezone.timedelta(hours=12)

    cotisations = Cotisation.objects.filter(
        statut='active',
        date_expiration__lte=dans_12h,
        date_expiration__gte=maintenant,
        rappel_envoye=False,
        supprime=False
    )

    for cot in cotisations:
        manquants = cot.nombre_participants - cot.participants_payes
        if manquants <= 0:
            continue

        msg = (
            f"Rappel Kotizo : La cotisation '{cot.nom}' expire dans moins de 12h.\n"
            f"{manquants} participant(s) manquant(s).\n"
            f"Lien : {cot.deep_link}"
        )

        try:
            envoyer_email(
                cot.createur.email,
                f"Rappel : {cot.nom} expire bientot",
                f"<p>{msg}</p>"
            )
            if cot.createur.whatsapp_numero:
                envoyer_message(cot.createur.whatsapp_numero, msg)
        except Exception as e:
            logger.error('rappel_echec', {'cotisation': str(cot.id), 'erreur': str(e)})

        cot.rappel_envoye = True
        cot.save(update_fields=['rappel_envoye'])

    logger.info('rappels_envoyes', {'nb': cotisations.count()})


@shared_task
def mettre_a_jour_fenetre():
    logger.info('fenetre_glissante_mise_a_jour', {})


@shared_task
def finaliser_cotisation(cotisation_id):
    from .models import Cotisation
    from paiements.models import Transaction
    from notifications.models import Notification
    from core.whatsapp import envoyer_message
    import requests
    from django.conf import settings

    try:
        cot = Cotisation.objects.get(id=cotisation_id)
        if cot.statut == 'complete':
            return

        cot.statut = 'complete'
        cot.save(update_fields=['statut'])

        cot.createur.nb_cotisations_completes += 1
        cot.createur.save(update_fields=['nb_cotisations_completes'])

        logger.info('cotisation_complete', {'cotisation_id': str(cotisation_id)})

        Notification.objects.create(
            user=cot.createur,
            type_notification='cotisation_complete',
            titre='Cotisation complete !',
            message=f'Felicitations ! "{cot.nom}" est complete. Reversement en cours.'
        )

        for part in cot.participations.filter(statut='paye'):
            Notification.objects.create(
                user=part.participant,
                type_notification='cotisation_complete',
                titre='Cotisation complete',
                message=f'La cotisation "{cot.nom}" est complete !'
            )

    except Cotisation.DoesNotExist:
        logger.error('cotisation_introuvable', {'id': str(cotisation_id)})
