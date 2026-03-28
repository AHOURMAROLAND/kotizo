from django.db import models

class Paiement(models.Model):
    class Type(models.TextChoices):
        AVANCE = 'AVANCE', 'Avance'
        TOTAL = 'TOTAL', 'Total'
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        SUCCES = 'SUCCES', 'Succes'
        ECHEC = 'ECHEC', 'Echec'
    
    type_paiement = models.CharField(max_length=20, choices=Type.choices)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    token_paydunya = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_paiement} - {self.montant}"
