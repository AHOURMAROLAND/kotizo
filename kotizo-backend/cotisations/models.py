import uuid
from django.db import models
from django.utils import timezone
from users.models import User


class Cotisation(models.Model):

    STATUT_CHOICES = [
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('expiree', 'Expiree'),
        ('stoppee', 'Stoppee'),
    ]

    DUREE_CHOICES = [3, 7, 14, 21, 30]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createur = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cotisations_creees')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    montant_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    nombre_participants = models.IntegerField()
    participants_payes = models.IntegerField(default=0)
    montant_collecte = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nb_jours = models.IntegerField()
    date_creation = models.DateTimeField(default=timezone.now)
    date_expiration = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    slug = models.CharField(max_length=20, unique=True)
    deep_link = models.CharField(max_length=100)
    qr_token = models.TextField(blank=True)
    prix_modifiable = models.BooleanField(default=False)
    numero_receveur = models.CharField(max_length=20)
    sendavapay_invoice_url = models.URLField(blank=True)
    rappel_envoye = models.BooleanField(default=False)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)
    supprime_par = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='cotisations_supprimees'
    )
    date_stop = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cotisations'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['createur', 'statut']),
            models.Index(fields=['date_expiration']),
            models.Index(fields=['supprime']),
        ]

    def __str__(self):
        return f"{self.nom} — @{self.createur.pseudo}"

    def progression(self):
        if self.nombre_participants == 0:
            return 0
        return round((self.participants_payes / self.nombre_participants) * 100, 1)

    def peut_etre_supprimee(self):
        if self.statut not in ['stoppee', 'expiree', 'complete']:
            return False
        if self.date_stop:
            delai = self.date_stop + timezone.timedelta(hours=48)
            return timezone.now() >= delai
        return True

    def est_active(self):
        return self.statut == 'active' and timezone.now() < self.date_expiration


class Participation(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Paye'),
        ('rembourse', 'Rembourse'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.PROTECT, related_name='participations')
    participant = models.ForeignKey(User, on_delete=models.PROTECT, related_name='participations')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    montant_par_unite = models.DecimalField(max_digits=12, decimal_places=2)
    nb_unites = models.IntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_participation = models.DateTimeField(default=timezone.now)
    rang_paiement = models.IntegerField(default=0)
    sendavapay_token = models.CharField(max_length=255, blank=True)
    participation_id = models.CharField(max_length=20, unique=True)
    qr_token = models.TextField(blank=True)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'participations'
        unique_together = [['cotisation', 'participant']]
        indexes = [
            models.Index(fields=['cotisation', 'statut']),
            models.Index(fields=['participant']),
        ]

    def __str__(self):
        return f"@{self.participant.pseudo} -> {self.cotisation.nom}"


class Commentaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    message = models.TextField()
    reponse_admin = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_reponse = models.DateTimeField(null=True, blank=True)
    supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'commentaires'
        ordering = ['-date_creation']

    def peut_commenter(self):
        delai = self.date_creation + timezone.timedelta(days=60)
        return timezone.now() <= delai


class NotationCreateur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE, related_name='notations')
    noteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_donnees')
    note = models.IntegerField()
    commentaire = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notations_createurs'
        unique_together = [['cotisation', 'noteur']]

    def save(self, *args, **kwargs):
        if not (1 <= self.note <= 5):
            raise ValueError("Note doit etre entre 1 et 5.")
        super().save(*args, **kwargs)
        self._mettre_a_jour_moyenne()

    def _mettre_a_jour_moyenne(self):
        createur = self.cotisation.createur
        toutes_notes = NotationCreateur.objects.filter(
            cotisation__createur=createur
        )
        if toutes_notes.exists():
            moyenne = sum(n.note for n in toutes_notes) / toutes_notes.count()
            createur.note_moyenne = round(moyenne, 1)
            createur.nb_notes_recues = toutes_notes.count()
            createur.save(update_fields=['note_moyenne', 'nb_notes_recues'])
