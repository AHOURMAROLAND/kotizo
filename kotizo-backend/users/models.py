import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, pseudo, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, pseudo=pseudo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pseudo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('admin_role', 'super_admin')
        return self.create_user(email, pseudo, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    NIVEAU_CHOICES = [
        ('basique', 'Basique'),
        ('verifie', 'Verifie'),
        ('business', 'Business'),
    ]

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('banni', 'Banni'),
        ('supprime', 'Supprime'),
    ]

    ADMIN_ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('moderateur', 'Moderateur'),
        ('support', 'Support'),
        ('finance', 'Finance'),
        ('verification', 'Verification'),
        ('lecteur', 'Lecteur'),
    ]

    THEME_CHOICES = [
        ('bleu', 'Bleu Classic'),
        ('vert', 'Vert Afrique'),
        ('violet', 'Violet Premium'),
    ]

    MODE_CHOICES = [
        ('sombre', 'Sombre'),
        ('clair', 'Clair'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    pseudo = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    whatsapp_numero = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)

    email_verifie = models.BooleanField(default=False)
    whatsapp_verifie = models.BooleanField(default=False)

    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='basique')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')

    identite_verifiee = models.BooleanField(default=False)
    numero_cni_hash = models.CharField(max_length=64, blank=True)
    photo_cni_recto = models.URLField(blank=True)
    photo_cni_verso = models.URLField(blank=True)
    statut_verification = models.CharField(
        max_length=20,
        choices=[('non_soumis', 'Non soumis'), ('en_attente', 'En attente'),
                 ('approuve', 'Approuve'), ('rejete', 'Rejete')],
        default='non_soumis'
    )
    nom_verrouille = models.BooleanField(default=False)
    prenom_verrouille = models.BooleanField(default=False)

    date_limite_verification = models.DateTimeField(null=True, blank=True)

    code_parrainage = models.CharField(max_length=8, unique=True, blank=True)
    parrain = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='filleuls'
    )
    nb_parrainages_actifs = models.IntegerField(default=0)

    note_moyenne = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    nb_notes_recues = models.IntegerField(default=0)
    nb_cotisations_completes = models.IntegerField(default=0)

    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='bleu')
    mode_preference = models.CharField(max_length=10, choices=MODE_CHOICES, default='sombre')

    fcm_token = models.TextField(blank=True)
    ville_approx = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=2, default='TG')

    admin_role = models.CharField(
        max_length=20, choices=ADMIN_ROLE_CHOICES,
        null=True, blank=True
    )

    date_inscription = models.DateTimeField(default=timezone.now)
    date_suppression = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pseudo', 'nom', 'prenom']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['pseudo']),
            models.Index(fields=['telephone']),
            models.Index(fields=['niveau']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"@{self.pseudo} ({self.email})"

    def age(self):
        if not self.date_naissance:
            return None
        today = timezone.now().date()
        age = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            age -= 1
        return age

    def est_banni(self):
        return self.statut == 'banni'

    def peut_cotiser(self):
        return self.statut == 'actif' and self.is_active


class VerificationObligatoire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verif_obligatoire')
    date_limite = models.DateTimeField()
    notif_envoyee = models.BooleanField(default=False)
    compte_ferme = models.BooleanField(default=False)

    class Meta:
        db_table = 'verification_obligatoire'


class SessionDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_connexion = models.DateTimeField(default=timezone.now)
    date_derniere_activite = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'session_devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
