import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('kotizo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expirer-quickpay-5min': {
        'task': 'quickpay.tasks.expirer_quickpay',
        'schedule': 300,
    },
    'ping-bot-whatsapp-5min': {
        'task': 'notifications.tasks.ping_bot_whatsapp',
        'schedule': 300,
    },
    'detection-fraude-30min': {
        'task': 'admin_panel.tasks.detection_fraude',
        'schedule': 1800,
    },
    'expirer-cotisations-1h': {
        'task': 'cotisations.tasks.expirer_cotisations',
        'schedule': 3600,
    },
    'fenetre-glissante-1h': {
        'task': 'cotisations.tasks.mettre_a_jour_fenetre',
        'schedule': 3600,
    },
    'comptes-non-verifies-1h': {
        'task': 'users.tasks.supprimer_comptes_non_verifies',
        'schedule': 3600,
    },
    'rappels-cotisations-6h': {
        'task': 'cotisations.tasks.envoyer_rappels',
        'schedule': 21600,
    },
    'rapport-journalier-20h': {
        'task': 'admin_panel.tasks.rapport_journalier',
        'schedule': crontab(hour=20, minute=0),
    },
    'reset-compteurs-email-minuit': {
        'task': 'notifications.tasks.reset_compteurs_email',
        'schedule': crontab(hour=0, minute=0),
    },
    'reset-compteurs-ia-minuit': {
        'task': 'agent_ia.tasks.reset_compteurs_ia',
        'schedule': crontab(hour=0, minute=0),
    },
    'verification-obligatoire-minuit': {
        'task': 'users.tasks.verifier_comptes_obligatoires',
        'schedule': crontab(hour=0, minute=0),
    },
}
