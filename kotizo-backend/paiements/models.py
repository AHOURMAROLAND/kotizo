from django.db import models
from django.conf import settings
import uuid


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('payin', 'PayIn'),
        ('payout', 'PayOut'),
        ('frais_verification', 'Frais verification'),
        ('frais_business', 'Frais business'),
    ]
    STATUT_CHOICES = [
        ('initie', 'Initie'),
        ('en_attente', 'En attente'),
        ('complete', 'Complete'),
        ('echoue', 'Echoue'),
        ('rembourse', 'Rembourse'),
    ]
    SOURCE_CHOICES = [
        ('cotisation', 'Cotisation'),
        ('quickpay', 'Quick Pay'),
        ('verification', 'Verification'),
        ('business', 'Business'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=30, choices=TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=100, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    frais_kotizo = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    frais_paydunya = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_net = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='initie')
    paydunya_token = models.CharField(max_length=200, blank=True)
    paydunya_invoice_token = models.CharField(max_length=200, blank=True)
    telephone_receveur = models.CharField(max_length=20, blank=True)
    operateur = models.CharField(max_length=20, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_completion = models.DateTimeField(null=True, blank=True)
    webhook_recu = models.BooleanField(default=False)
    webhook_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-date_creation']


class DemandeRemboursement(models.Model):
    RAISON_CHOICES = [
        ('erreur_technique', 'Erreur technique'),
        ('double_paiement', 'Double paiement'),
        ('fraude_confirmee', 'Fraude confirmee'),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepte'),
        ('rejete', 'Rejete'),
        ('rembourse', 'Rembourse'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES)
    description = models.TextField()
    preuves_urls = models.JSONField(default=list)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    note_admin = models.TextField(blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'demandes_remboursement'