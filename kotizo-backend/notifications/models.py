from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('paiement_recu', 'Paiement recu'),
        ('cotisation_complete', 'Cotisation complete'),
        ('cotisation_expiree', 'Cotisation expiree'),
        ('verification_approuvee', 'Verification approuvee'),
        ('verification_rejetee', 'Verification rejetee'),
        ('sanction', 'Sanction'),
        ('remboursement', 'Remboursement'),
        ('rappel', 'Rappel'),
        ('systeme', 'Systeme'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-date_creation']