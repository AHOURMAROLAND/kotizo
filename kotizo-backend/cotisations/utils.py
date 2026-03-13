import random
import string
from .models import Cotisation


def generer_slug():
    while True:
        slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Cotisation.objects.filter(slug=slug).exists():
            return slug


def detecter_operateur(numero):
    numero = numero.replace('+228', '').replace(' ', '')
    if numero.startswith(('9', '8')):
        return 'moov-togo'
    if numero.startswith('7'):
        return 't-money-togo'
    return 'moov-togo'


def calculer_frais_kotizo(montant):
    montant = int(montant)
    if montant <= 5000:
        return 250
    if montant <= 10000:
        return 500
    return 1000