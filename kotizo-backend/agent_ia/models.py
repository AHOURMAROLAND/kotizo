from django.db import models

class AgentIA(models.Model):
    nom = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
