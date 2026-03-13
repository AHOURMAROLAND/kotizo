from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VerificationIdentite, DemandeBusinessLevel

User = get_user_model()


class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    cgu_acceptees = serializers.BooleanField()
    politique_confidentialite = serializers.BooleanField(write_only=True)
    age_confirme = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'nom', 'prenom', 'telephone', 'pays',
                  'password', 'password_confirm',
                  'cgu_acceptees', 'politique_confidentialite', 'age_confirme']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas'})
        if not data.get('cgu_acceptees'):
            raise serializers.ValidationError({'cgu_acceptees': 'Vous devez accepter les CGU'})
        if not data.get('politique_confidentialite'):
            raise serializers.ValidationError({'politique_confidentialite': 'Vous devez accepter la politique de confidentialite'})
        if not data.get('age_confirme'):
            raise serializers.ValidationError({'age_confirme': 'Vous devez confirmer avoir 18 ans ou plus'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data.pop('politique_confidentialite')
        validated_data.pop('age_confirme')
        password = validated_data.pop('password')

        from django.utils import timezone
        import secrets

        user = User(**validated_data)
        user.set_password(password)
        user.cgu_version = '1.0'
        user.cgu_date_acceptation = timezone.now()
        user.token_verification_email = secrets.token_urlsafe(32)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nom', 'prenom', 'telephone',
                  'pays', 'niveau', 'photo', 'email_verifie',
                  'date_inscription']
        read_only_fields = ['id', 'niveau', 'email_verifie', 'date_inscription']


class UserProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nom', 'prenom', 'telephone', 'photo']


class VerificationIdentiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationIdentite
        fields = ['type_document', 'photo_recto', 'photo_verso',
                  'liveness_valide', 'statut', 'date_soumission']
        read_only_fields = ['statut', 'date_soumission']


class DemandeBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeBusinessLevel
        fields = ['statut', 'date_approbation', 'date_expiration_gratuite',
                  'paiement_effectue', 'date_demande']
        read_only_fields = fields