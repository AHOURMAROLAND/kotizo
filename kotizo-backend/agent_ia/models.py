from django.db import models
from django.conf import settings
import uuid


class ConversationIA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations_ia')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_activite = models.DateTimeField(auto_now=True)
    nb_messages = models.IntegerField(default=0)

    class Meta:
        db_table = 'conversations_ia'
        ordering = ['-date_derniere_activite']


class MessageIA(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(ConversationIA, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenu = models.TextField()
    image_url = models.URLField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages_ia'
        ordering = ['date_creation']


class TicketSupport(models.Model):
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Resolu'),
        ('ferme', 'Ferme'),
    ]
    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    sujet = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale')
    cree_par_ia = models.BooleanField(default=False)
    conversation = models.ForeignKey(ConversationIA, on_delete=models.SET_NULL, null=True, blank=True)
    note_admin = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tickets_support'
        ordering = ['-date_creation']