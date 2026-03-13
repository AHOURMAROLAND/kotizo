from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from core.logger import logger


@shared_task
def envoyer_email_verification(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        lien = f'https://api.kotizo.app/auth/verifier-email/{user.token_verification_email}/'
        send_mail(
            subject='Verifiez votre adresse email - Kotizo',
            message=f'Bonjour {user.prenom},\n\nCliquez sur ce lien pour verifier votre email :\n{lien}\n\nLien valable 24h.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Email verification envoye', user_id=str(user.id))
    except Exception as e:
        logger.error(f'Erreur envoi email verification : {str(e)}')


@shared_task
def reset_compteurs_quotidiens():
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    User = get_user_model()
    User.objects.all().update(cotisations_creees_aujourd_hui=0, date_reset_compteur=timezone.now().date())
    logger.info('Compteurs quotidiens reinitialises')