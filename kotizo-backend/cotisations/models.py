from django.db import models

class Cotisation(models.Model):
    nom = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    frequence = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
