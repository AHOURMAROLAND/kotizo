import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.cache import cache
from django.conf import settings
from core.logger import KotizoLogger

logger = KotizoLogger('email_router')

FOURNISSEURS = [
    {'nom': 'gmail',   'limite': 500},
    {'nom': 'brevo',   'limite': 300},
    {'nom': 'mailjet', 'limite': 200},
    {'nom': 'resend',  'limite': 100},
]


def get_compteur(nom):
    return cache.get(f'email_compteur_{nom}', 0)


def incrementer_compteur(nom):
    key = f'email_compteur_{nom}'
    val = cache.get(key, 0) + 1
    cache.set(key, val, timeout=86400)


def choisir_fournisseur():
    for f in FOURNISSEURS:
        if get_compteur(f['nom']) < f['limite']:
            return f['nom']
    return None


def envoyer_email(destinataire, sujet, html, texte=None):
    fournisseur = choisir_fournisseur()
    if not fournisseur:
        logger.error('email_tous_fournisseurs_satures', {'destinataire': destinataire})
        return False
    try:
        if fournisseur == 'gmail':
            _envoyer_gmail(destinataire, sujet, html, texte)
        elif fournisseur == 'brevo':
            _envoyer_brevo(destinataire, sujet, html)
        elif fournisseur == 'mailjet':
            _envoyer_mailjet(destinataire, sujet, html)
        elif fournisseur == 'resend':
            _envoyer_resend(destinataire, sujet, html)
        incrementer_compteur(fournisseur)
        logger.info('email_envoye', {
            'fournisseur': fournisseur,
            'destinataire': destinataire,
            'sujet': sujet
        })
        return True
    except Exception as e:
        logger.error('email_echec', {
            'fournisseur': fournisseur,
            'erreur': str(e)
        })
        return False


def _envoyer_gmail(destinataire, sujet, html, texte=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = sujet
    msg['From'] = settings.DEFAULT_FROM_EMAIL
    msg['To'] = destinataire
    if texte:
        msg.attach(MIMEText(texte, 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
        server.sendmail(settings.GMAIL_USER, destinataire, msg.as_string())


def _envoyer_brevo(destinataire, sujet, html):
    import requests
    requests.post(
        'https://api.brevo.com/v3/smtp/email',
        headers={
            'api-key': settings.BREVO_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'sender': {'email': settings.GMAIL_USER, 'name': 'Kotizo'},
            'to': [{'email': destinataire}],
            'subject': sujet,
            'htmlContent': html
        },
        timeout=10
    )


def _envoyer_mailjet(destinataire, sujet, html):
    import requests
    requests.post(
        'https://api.mailjet.com/v3.1/send',
        auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
        json={
            'Messages': [{
                'From': {'Email': settings.GMAIL_USER, 'Name': 'Kotizo'},
                'To': [{'Email': destinataire}],
                'Subject': sujet,
                'HTMLPart': html
            }]
        },
        timeout=10
    )


def _envoyer_resend(destinataire, sujet, html):
    import requests
    requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {settings.RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': settings.DEFAULT_FROM_EMAIL,
            'to': [destinataire],
            'subject': sujet,
            'html': html
        },
        timeout=10
    )
