import requests
from django.conf import settings
from core.logger import logger


def envoyer_push(fcm_token, titre, message, data=None):
    if not fcm_token or not settings.FCM_SERVER_KEY:
        return False

    payload = {
        'to': fcm_token,
        'notification': {
            'title': titre,
            'body': message,
            'sound': 'default',
        },
        'data': data or {},
    }

    try:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            json=payload,
            headers={
                'Authorization': f'key={settings.FCM_SERVER_KEY}',
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f'Erreur envoi push : {str(e)}')
        return False


def creer_notification(user, type_notification, titre, message, data=None):
    from .models import Notification
    notification = Notification.objects.create(
        user=user,
        type_notification=type_notification,
        titre=titre,
        message=message,
        data=data or {},
    )
    envoyer_push(user.fcm_token, titre, message, data)
    return notification