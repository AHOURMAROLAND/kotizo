from celery import shared_task
from django.utils import timezone
from core.logger import logger


@shared_task
def traiter_paiement_confirme(transaction_id):
    from .models import Transaction
    from cotisations.models import Participation, Cotisation
    from .utils import initier_payout

    try:
        transaction = Transaction.objects.get(id=transaction_id)
        participation = Participation.objects.get(
            paydunya_token=transaction.paydunya_token
        )
        cotisation = participation.cotisation

        participation.statut = 'paye'
        participation.date_paiement = timezone.now()
        participation.save()

        cotisation.participants_payes += 1
        cotisation.montant_collecte += participation.montant
        if cotisation.is_complete():
            cotisation.statut = 'complete'
        cotisation.save()

        frais_paydunya = int(cotisation.montant_unitaire * 0.02)
        montant_net = int(cotisation.montant_unitaire) - frais_paydunya

        payout_transaction = Transaction.objects.create(
            user=cotisation.createur,
            type_transaction='payout',
            source='cotisation',
            source_id=str(cotisation.id),
            montant=cotisation.montant_unitaire,
            frais_paydunya=frais_paydunya,
            montant_net=montant_net,
            statut='initie',
            telephone_receveur=cotisation.numero_receveur,
            operateur=cotisation.operateur_receveur,
        )

        result = initier_payout(
            montant=montant_net,
            telephone=cotisation.numero_receveur,
            operateur=cotisation.operateur_receveur,
            description=f'Reversement cotisation {cotisation.nom}',
            reference=str(payout_transaction.id),
        )

        if result.get('response_code') == '00':
            payout_transaction.statut = 'en_attente'
            logger.paiement('PayOut initie', user_id=str(cotisation.createur.id), montant=montant_net)
        else:
            payout_transaction.statut = 'echoue'
            logger.error(f'PayOut echoue : {result}')

        payout_transaction.save()

        from notifications.tasks import envoyer_notification_paiement
        envoyer_notification_paiement.delay(str(participation.id))

    except Exception as e:
        logger.error(f'Erreur traitement paiement confirme : {str(e)}')


@shared_task
def verifier_payout_pending():
    from .models import Transaction
    from .utils import verifier_statut_payout

    pending = Transaction.objects.filter(
        type_transaction='payout',
        statut='en_attente',
    )
    for transaction in pending:
        try:
            result = verifier_statut_payout(str(transaction.id))
            if result.get('status') == 'SUCCESS':
                transaction.statut = 'complete'
                transaction.date_completion = timezone.now()
                transaction.save()
                logger.paiement('PayOut complete via verification', user_id=str(transaction.user.id))
        except Exception as e:
            logger.error(f'Erreur verification payout {transaction.id} : {str(e)}')