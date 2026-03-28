from django.db import models

class QuickPay(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, default='EN_ATTENTE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference
