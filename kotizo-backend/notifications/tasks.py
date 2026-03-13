from celery import shared_task
from core.logger import logger


@shared_task
def envoyer_notification_paiement(participation_id):
    from cotisations.models import Participation
    from .utils import creer_notification

    try:
        participation = Participation.objects.select_related(
            'cotisation', 'cotisation__createur', 'participant'
        ).get(id=participation_id)

        cotisation = participation.cotisation

        creer_notification(
            user=participation.participant,
            type_notification='paiement_recu',
            titre='Paiement confirme',
            message=f'Votre paiement de {participation.montant} FCFA pour "{cotisation.nom}" a ete confirme.',
            data={'cotisation_slug': cotisation.slug},
        )

        creer_notification(
            user=cotisation.createur,
            type_notification='paiement_recu',
            titre='Nouveau paiement recu',
            message=f'{participation.participant.prenom} a paye pour "{cotisation.nom}". Reversement en cours.',
            data={'cotisation_slug': cotisation.slug},
        )

        if cotisation.is_complete():
            creer_notification(
                user=cotisation.createur,
                type_notification='cotisation_complete',
                titre='Cotisation complete !',
                message=f'Tous les participants ont paye pour "{cotisation.nom}".',
                data={'cotisation_slug': cotisation.slug},
            )

    except Exception as e:
        logger.error(f'Erreur notification paiement : {str(e)}')


@shared_task
def envoyer_notification_verification(user_id, approuvee):
    from django.contrib.auth import get_user_model
    from .utils import creer_notification

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        if approuvee:
            creer_notification(
                user=user,
                type_notification='verification_approuvee',
                titre='Compte verifie !',
                message='Votre identite a ete verifiee. Vous passez au niveau Verifie.',
            )
        else:
            creer_notification(
                user=user,
                type_notification='verification_rejetee',
                titre='Verification rejetee',
                message='Votre demande de verification a ete rejetee. Contactez le support.',
            )
    except Exception as e:
        logger.error(f'Erreur notification verification : {str(e)}')


@shared_task
def envoyer_notification_sanction(user_id, niveau_sanction, raison):
    from django.contrib.auth import get_user_model
    from .utils import creer_notification

    User = get_user_model()
    niveaux = {
        0: 'Avertissement',
        1: 'Restriction legere',
        2: 'Restriction moyenne',
        3: 'Degradation de compte',
        4: 'Fermeture temporaire',
        5: 'Bannissement',
    }
    try:
        user = User.objects.get(id=user_id)
        creer_notification(
            user=user,
            type_notification='sanction',
            titre=f'Sanction : {niveaux.get(niveau_sanction, "")}',
            message=f'Raison : {raison}',
        )
    except Exception as e:
        logger.error(f'Erreur notification sanction : {str(e)}')


@shared_task
def envoyer_rapport_journalier():
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    from cotisations.models import Cotisation, Participation
    from paiements.models import Transaction

    User = get_user_model()
    aujourd_hui = timezone.now().date()

    users_actifs = User.objects.filter(
        transactions__date_creation__date=aujourd_hui
    ).distinct()

    for user in users_actifs:
        try:
            transactions = Transaction.objects.filter(
                user=user,
                date_creation__date=aujourd_hui,
                statut='complete',
            )
            if not transactions.exists():
                continue

            total_payin = sum(
                t.montant for t in transactions if t.type_transaction == 'payin'
            )
            total_payout = sum(
                t.montant for t in transactions if t.type_transaction == 'payout'
            )

            send_mail(
                subject=f'Votre rapport Kotizo du {aujourd_hui.strftime("%d/%m/%Y")}',
                message=(
                    f'Bonjour {user.prenom},\n\n'
                    f'Resume de votre journee sur Kotizo :\n\n'
                    f'Paiements effectues : {total_payin} FCFA\n'
                    f'Reversements recus : {total_payout} FCFA\n\n'
                    f'Merci d\'utiliser Kotizo.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            logger.info(f'Rapport journalier envoye', user_id=str(user.id))

        except Exception as e:
            logger.error(f'Erreur rapport journalier user {user.id} : {str(e)}')