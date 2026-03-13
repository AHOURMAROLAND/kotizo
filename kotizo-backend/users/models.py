from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    NIVEAU_CHOICES = [
        ('basique', 'Basique'),
        ('verifie', 'Verifie'),
        ('business', 'Business'),
    ]
    PAYS_CHOICES = [
        ('TG', 'Togo'),
        ('BJ', 'Benin'),
        ('CI', 'Cote d\'Ivoire'),
        ('SN', 'Senegal'),
        ('GH', 'Ghana'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    pays = models.CharField(max_length=5, choices=PAYS_CHOICES, default='TG')
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='basique')
    photo = models.URLField(blank=True)

    email_verifie = models.BooleanField(default=False)
    token_verification_email = models.CharField(max_length=100, blank=True)

    cgu_acceptees = models.BooleanField(default=False)
    cgu_version = models.CharField(max_length=10, blank=True)
    cgu_date_acceptation = models.DateTimeField(null=True, blank=True)
    cgu_ip_acceptation = models.GenericIPAddressField(null=True, blank=True)

    cotisations_creees_aujourd_hui = models.IntegerField(default=0)
    date_reset_compteur = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion_app = models.DateTimeField(null=True, blank=True)

    fcm_token = models.TextField(blank=True)
    device_id = models.CharField(max_length=200, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    def get_limite_cotisations(self):
        limites = {'basique': 5, 'verifie': 20, 'business': None}
        return limites.get(self.niveau)


class VerificationIdentite(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuve'),
        ('rejete', 'Rejete'),
    ]
    TYPE_DOC_CHOICES = [
        ('cni', 'CNI'),
        ('passeport', 'Passeport'),
        ('consulaire', 'Carte consulaire'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')
    type_document = models.CharField(max_length=20, choices=TYPE_DOC_CHOICES)
    photo_recto = models.URLField()
    photo_verso = models.URLField()
    liveness_video = models.URLField(blank=True)
    liveness_valide = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    note_admin = models.TextField(blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    paiement_effectue = models.BooleanField(default=False)

    class Meta:
        db_table = 'verifications_identite'


class DemandeBusinessLevel(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuve'),
        ('rejete', 'Rejete'),
        ('expire', 'Expire'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_business')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_approbation = models.DateTimeField(null=True, blank=True)
    date_expiration_gratuite = models.DateTimeField(null=True, blank=True)
    paiement_effectue = models.BooleanField(default=False)
    note_admin = models.TextField(blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'demandes_business'


class BlacklistDevice(models.Model):
    device_id = models.CharField(max_length=200, unique=True)
    raison = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blacklist_devices'


class BlacklistNumero(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    raison = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blacklist_numeros'
class Sanction(models.Model):
    NIVEAU_CHOICES = [
        (0, 'Avertissement'),
        (1, 'Restriction legere'),
        (2, 'Restriction moyenne'),
        (3, 'Degradation compte'),
        (4, 'Fermeture temporaire'),
        (5, 'Bannissement permanent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sanctions')
    niveau = models.IntegerField(choices=NIVEAU_CHOICES)
    raison = models.TextField()
    appliquee_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sanctions_appliquees')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    contestee = models.BooleanField(default=False)
    note_contestation = models.TextField(blank=True)

    class Meta:
        db_table = 'sanctions'
        ordering = ['-date_debut']


class AlerteFraude(models.Model):
    TYPE_CHOICES = [
        ('multi_comptes', 'Multi comptes'),
        ('signalements_multiples', 'Signalements multiples'),
        ('creation_rapide', 'Creation rapide'),
        ('numero_suspect', 'Numero suspect'),
        ('ip_suspecte', 'IP suspecte'),
        ('fraude_paydunya', 'Fraude PayDunya'),
    ]
    STATUT_CHOICES = [
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En cours'),
        ('resolue', 'Resolue'),
        ('faux_positif', 'Faux positif'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertes_fraude')
    type_alerte = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouvelle')
    data = models.JSONField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alertes_fraude'
        ordering = ['-date_creation']