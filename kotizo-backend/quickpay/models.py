from django.db import models
from django.conf import settings
import uuid


class QuickPay(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('paye', 'Paye'),
        ('expire', 'Expire'),
        ('annule', 'Annule'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quickpays_crees')
    code = models.CharField(max_length=10, unique=True)
    montant = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.CharField(max_length=200, blank=True)
    numero_receveur = models.CharField(max_length=20)
    operateur_receveur = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    date_paiement = models.DateTimeField(null=True, blank=True)
    payeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='quickpays_payes')
    paydunya_token = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'quickpay'
        ordering = ['-date_creation']