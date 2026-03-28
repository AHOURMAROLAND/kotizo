import hashlib
from datetime import date
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from .models import User, SessionDevice
from core.utils import generer_code_parrainage


class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirmer_password = serializers.CharField(write_only=True)
    cgu_acceptees = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'prenom', 'nom', 'pseudo', 'email',
            'telephone', 'whatsapp_numero', 'date_naissance',
            'password', 'confirmer_password', 'cgu_acceptees'
        ]

    def validate_date_naissance(self, value):
        today = date.today()
        age = today.year - value.year
        if (today.month, today.day) < (value.month, value.day):
            age -= 1
        if age < 16:
            raise serializers.ValidationError("Age minimum requis : 16 ans.")
        return value

    def validate_pseudo(self, value):
        if User.objects.filter(pseudo__iexact=value).exists():
            raise serializers.ValidationError("Ce pseudo est deja pris.")
        if len(value) > 20:
            raise serializers.ValidationError("Pseudo max 20 caracteres.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est deja utilise.")
        return value.lower()

    def validate_telephone(self, value):
        if not value.startswith('+228') or len(value) != 12:
            raise serializers.ValidationError("Format requis : +228XXXXXXXX")
        key = f'inscription_tentatives_{value}'
        tentatives = cache.get(key, 0)
        if tentatives >= 3:
            raise serializers.ValidationError(
                "Ce numero est bloque pendant 24h suite a trop de tentatives."
            )
        return value

    def validate(self, data):
        if not data.get('cgu_acceptees'):
            raise serializers.ValidationError("Vous devez accepter les CGU.")
        if data['password'] != data['confirmer_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmer_password')
        validated_data.pop('cgu_acceptees')
        password = validated_data.pop('password')

        code = generer_code_parrainage()
        while User.objects.filter(code_parrainage=code).exists():
            code = generer_code_parrainage()

        user = User(**validated_data)
        user.set_password(password)
        user.code_parrainage = code
        user.date_limite_verification = timezone.now() + timezone.timedelta(days=30)
        user.save()

        from .models import VerificationObligatoire
        VerificationObligatoire.objects.create(
            user=user,
            date_limite=user.date_limite_verification
        )

        return user


class ConnexionSerializer(serializers.Serializer):
    identifiant = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifiant = data['identifiant']
        password = data['password']

        user = None
        if '@' in identifiant:
            try:
                user = User.objects.get(email__iexact=identifiant)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = User.objects.get(pseudo__iexact=identifiant)
            except User.DoesNotExist:
                pass

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Identifiants incorrects.")

        if not user.is_active:
            raise serializers.ValidationError("Compte desactive.")

        if user.statut == 'banni':
            raise serializers.ValidationError("Compte banni.")

        if user.statut == 'supprime':
            raise serializers.ValidationError("Compte supprime.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'pseudo', 'nom', 'prenom',
            'telephone', 'whatsapp_numero', 'date_naissance',
            'niveau', 'statut', 'identite_verifiee',
            'statut_verification', 'note_moyenne',
            'nb_cotisations_completes', 'nb_notes_recues',
            'code_parrainage', 'nb_parrainages_actifs',
            'theme_preference', 'mode_preference',
            'date_inscription', 'pays', 'ville_approx',
        ]
        read_only_fields = [
            'id', 'email', 'niveau', 'statut',
            'identite_verifiee', 'statut_verification',
            'note_moyenne', 'nb_cotisations_completes',
            'nb_notes_recues', 'code_parrainage',
            'nb_parrainages_actifs', 'date_inscription',
        ]

    def validate_pseudo(self, value):
        user = self.context['request'].user
        if User.objects.filter(pseudo__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Ce pseudo est deja pris.")
        return value

    def validate_nom(self, value):
        user = self.context['request'].user
        if user.nom_verrouille:
            raise serializers.ValidationError("Nom verrouille apres verification.")
        return value

    def validate_prenom(self, value):
        user = self.context['request'].user
        if user.prenom_verrouille:
            raise serializers.ValidationError("Prenom verrouille apres verification.")
        return value


class UserPublicSerializer(serializers.ModelSerializer):
    note_affichee = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'pseudo', 'nom', 'prenom',
            'identite_verifiee', 'niveau',
            'note_affichee', 'nb_cotisations_completes',
            'date_inscription',
        ]

    def get_note_affichee(self, obj):
        if obj.nb_cotisations_completes >= 5:
            return float(obj.note_moyenne)
        return None


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['theme_preference', 'mode_preference']


class VerificationCNISerializer(serializers.Serializer):
    photo_recto = serializers.URLField()
    photo_verso = serializers.URLField()
    numero_carte = serializers.CharField(max_length=50)

    def validate_numero_carte(self, value):
        return hashlib.sha256(value.strip().encode()).hexdigest()


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionDevice
        fields = [
            'id', 'device_name', 'ip_address',
            'is_active', 'date_connexion', 'date_derniere_activite'
        ]
