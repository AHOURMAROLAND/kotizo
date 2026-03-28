import random
import time
import requests
from django.conf import settings
from core.logger import KotizoLogger

logger = KotizoLogger('whatsapp')


def _headers():
    return {
        'apikey': settings.EVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }


def _url(endpoint):
    return f"{settings.EVOLUTION_API_URL}/{endpoint}"


def envoyer_message(numero, message):
    time.sleep(random.uniform(3, 6))
    try:
        numero_formate = numero.replace('+', '') + '@s.whatsapp.net'
        response = requests.post(
            _url(f"message/sendText/{settings.EVOLUTION_INSTANCE}"),
            headers=_headers(),
            json={
                'number': numero_formate,
                'text': message
            },
            timeout=15
        )
        logger.info('whatsapp_envoye', {
            'numero': numero[:8] + '****',
            'status': response.status_code
        })
        return response.status_code == 201
    except Exception as e:
        logger.error('whatsapp_echec', {'erreur': str(e)})
        return False


def envoyer_message_banni(numero):
    message = (
        "Votre compte Kotizo est banni.\n"
        "Vous ne pouvez plus utiliser ce service.\n"
        "Pour contester, contactez le support."
    )
    return envoyer_message(numero, message)


def ping_instance():
    try:
        response = requests.get(
            _url(f"instance/fetchInstances"),
            headers=_headers(),
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def envoyer_broadcast(message, numeros):
    resultats = []
    for numero in numeros:
        ok = envoyer_message(numero, message)
        resultats.append({'numero': numero, 'ok': ok})
    return resultats
