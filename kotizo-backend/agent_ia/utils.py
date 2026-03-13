import re
import requests
from django.conf import settings
from core.logger import logger

MOTS_INTERDITS = [
    'ignore previous', 'ignore tes instructions', 'jailbreak',
    'prompt injection', 'system prompt', 'tu es maintenant',
    'oublie tes regles', 'act as', 'pretend you are',
]

SYSTEM_PROMPT = """
Tu es l'assistant virtuel de Kotizo, une application de cotisations collectives au Togo.

Regles absolues :
- Tu reponds UNIQUEMENT aux questions liees a Kotizo et ses fonctionnalites
- Tu ne fais JAMAIS de paiement directement
- Tu ne supprimes JAMAIS un compte
- Tu ne modifies JAMAIS un montant ou un numero receveur
- Tu ne reponds pas aux questions hors sujet Kotizo
- Tu reponds toujours en francais
- Tu es poli, clair et concis

Tu peux :
- Repondre aux questions sur l'application
- Aider a comprendre les cotisations et Quick Pay
- Creer des tickets support
- Expliquer les frais et niveaux
- Donner le statut des cotisations et paiements de l'utilisateur
"""


def detecter_injection(message):
    message_lower = message.lower()
    for mot in MOTS_INTERDITS:
        if mot in message_lower:
            return True
    return False


def masquer_donnees_sensibles(texte):
    texte = re.sub(r'\+?228\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}', '[NUMERO]', texte)
    texte = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', texte)
    return texte


def construire_contexte_user(user):
    from cotisations.models import Cotisation, Participation
    from paiements.models import Transaction

    cotisations_actives = Cotisation.objects.filter(
        createur=user, statut='active'
    ).count()

    participations_payees = Participation.objects.filter(
        participant=user, statut='paye'
    ).count()

    derniere_transaction = Transaction.objects.filter(
        user=user, statut='complete'
    ).first()

    return {
        'prenom': user.prenom,
        'niveau': user.niveau,
        'cotisations_actives': cotisations_actives,
        'participations_payees': participations_payees,
        'derniere_transaction_montant': str(derniere_transaction.montant) if derniere_transaction else None,
    }


def appeler_gemini(messages_historique, contexte_user):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}'

    contexte_str = f"""
Informations sur l'utilisateur connecte :
- Prenom : {contexte_user['prenom']}
- Niveau : {contexte_user['niveau']}
- Cotisations actives creees : {contexte_user['cotisations_actives']}
- Participations payees : {contexte_user['participations_payees']}
"""

    contents = []
    for msg in messages_historique:
        role = 'user' if msg['role'] == 'user' else 'model'
        contents.append({
            'role': role,
            'parts': [{'text': msg['contenu']}],
        })

    if contents and contents[0]['role'] == 'user':
        contents[0]['parts'][0]['text'] = (
            f"{SYSTEM_PROMPT}\n\n{contexte_str}\n\n"
            f"{contents[0]['parts'][0]['text']}"
        )

    payload = {
        'contents': contents,
        'generationConfig': {
            'maxOutputTokens': 500,
            'temperature': 0.3,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        texte = data['candidates'][0]['content']['parts'][0]['text']
        return masquer_donnees_sensibles(texte)
    except Exception as e:
        logger.error(f'Erreur appel Gemini : {str(e)}')
        return 'Desolee, je rencontre une difficulte technique. Veuillez reessayer.'