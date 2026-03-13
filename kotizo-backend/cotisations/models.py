from django.db import models
from django.conf import settings
import uuid


class Cotisation(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('expiree', 'Expiree'),
        ('suspendue', 'Suspendue'),
        ('annulee', 'Annulee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cotisations_creees')
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    montant_unitaire = models.DecimalField(max_digits=10, decimal_places=0)
    nombre_participants = models.IntegerField()
    numero_receveur = models.CharField(max_length=20)
    operateur_receveur = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    slug = models.CharField(max_length=20, unique=True)
    date_expiration = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    participants_payes = models.IntegerField(default=0)
    montant_collecte = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    pdf_participants_url = models.URLField(blank=True)

    class Meta:
        db_table = 'cotisations'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} - {self.createur}"

    def get_montant_total(self):
        return self.montant_unitaire * self.nombre_participants

    def is_complete(self):
        return self.participants_payes >= self.nombre_participants


class Participation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Paye'),
        ('echoue', 'Echoue'),
        ('rembourse', 'Rembourse'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='participations')
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant = models.DecimalField(max_digits=10, decimal_places=0)
    paydunya_token = models.CharField(max_length=200, blank=True)
    date_participation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    recu_confirme = models.BooleanField(default=False)
    date_confirmation_recu = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'participations'
        unique_together = ['cotisation', 'participant']


class Signalement(models.Model):
    RAISON_CHOICES = [
        ('arnaque', 'Arnaque'),
        ('contenu_inapproprie', 'Contenu inapproprie'),
        ('spam', 'Spam'),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('examine', 'Examine'),
        ('confirme', 'Confirme'),
        ('rejete', 'Rejete'),
    ]

    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='signalements')
    signaleur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_signalement = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signalements'
        unique_together = ['cotisation', 'signaleur']