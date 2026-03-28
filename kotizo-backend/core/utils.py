import random
import string
import hashlib
import json
import base64
from django.conf import settings


def generer_code(prefix, longueur=12):
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=longueur))
    return f"{prefix}-{code}"


def generer_slug_cotisation():
    return generer_code('KTZ', 12)


def generer_code_quickpay():
    return generer_code('QP', 8)


def generer_code_participation():
    return generer_code('PART', 8)


def generer_code_parrainage():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


def calculer_frais_kotizo(montant):
    return round(float(montant) * 0.005, 0)


def calculer_total_participant(montant):
    return round(float(montant) * 1.05, 0)


def calculer_montant_net(montant):
    return round(float(montant) - calculer_frais_kotizo(montant), 0)


def detecter_operateur(telephone):
    numero = telephone.replace('+228', '').replace(' ', '')
    prefixe = int(numero[:2])
    moov = [90, 91, 92, 93, 94, 95, 96, 97]
    mixx = [70, 71, 72, 79]
    tmoney = [98, 99]
    if prefixe in moov:
        return 'MOOV_TOGO'
    if prefixe in mixx:
        return 'MIXX_TOGO'
    if prefixe in tmoney:
        return 'TMONEY_TOGO'
    raise ValueError(f"Operateur inconnu pour le prefixe {prefixe}")


def generer_qr_token(data: dict) -> str:
    try:
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        secret = settings.KOTIZO_QR_SECRET.encode()[:32]
        payload = json.dumps(data, ensure_ascii=False).encode()
        cipher = AES.new(secret, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(payload)
        result = cipher.nonce + tag + ciphertext
        return base64.urlsafe_b64encode(result).decode()
    except Exception:
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()


def decoder_qr_token(token: str) -> dict:
    try:
        from Crypto.Cipher import AES
        secret = settings.KOTIZO_QR_SECRET.encode()[:32]
        raw = base64.urlsafe_b64decode(token.encode())
        nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
        cipher = AES.new(secret, AES.MODE_EAX, nonce)
        payload = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(payload)
    except Exception:
        raise ValueError("Token QR invalide ou corrompu")


def masquer_numero(telephone):
    if len(telephone) < 8:
        return telephone
    return telephone[:6] + 'XX' + telephone[-2:]


def formater_montant(montant):
    return f"{int(montant):,}".replace(',', ' ') + ' FCFA'
