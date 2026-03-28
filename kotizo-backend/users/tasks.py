from celery import shared_task
from django.utils import timezone
from core.logger import KotizoLogger

logger = KotizoLogger('users.tasks')


@shared_task
def supprimer_comptes_non_verifies():
    from .models import User, VerificationObligatoire
    from core.whatsapp import envoyer_message
    from core.email_router import envoyer_email

    now = timezone.now()
    verifs = VerificationObligatoire.objects.filter(
        date_limite__lte=now,
        compte_ferme=False,
        user__identite_verifiee=False,
        user__is_active=True
    )

    for v in verifs:
        user = v.user
        user.is_active = False
        user.statut = 'supprime'
        user.date_suppression = now
        user.save()

        v.compte_ferme = True
        v.save()

        logger.info('compte_supprime_non_verifie', {'user_id': str(user.id)})

        try:
            envoyer_email(
                user.email,
                'Compte Kotizo supprime',
                f'<p>Bonjour {user.prenom}, votre compte a ete supprime car vous '
                f'n avez pas soumis vos documents de verification dans le delai imparti.</p>'
            )
        except Exception:
            pass


@shared_task
def verifier_comptes_obligatoires():
    from .models import User
    from core.whatsapp import envoyer_message
    from core.email_router import envoyer_email

    now = timezone.now()
    dans_7j = now + timezone.timedelta(days=7)

    users_a_avertir = User.objects.filter(
        identite_verifiee=False,
        is_active=True,
        statut='actif',
        date_limite_verification__lte=dans_7j,
        date_limite_verification__gte=now
    )

    for user in users_a_avertir:
        try:
            envoyer_email(
                user.email,
                'Verification requise — Kotizo',
                f'<p>Bonjour {user.prenom}, vous avez 7 jours pour verifier '
                f'votre identite sinon votre compte sera supprime.</p>'
            )
        except Exception:
            pass
