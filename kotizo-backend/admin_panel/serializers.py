from rest_framework import serializers
from django.contrib.auth import get_user_model
from cotisations.models import Cotisation, Signalement
from paiements.models import Transaction, DemandeRemboursement
from users.models import VerificationIdentite, DemandeBusinessLevel, Sanction, AlerteFraude
from agent_ia.models import TicketSupport

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    nb_cotisations = serializers.SerializerMethodField()
    nb_transactions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'nom', 'prenom', 'telephone', 'pays',
                  'niveau', 'email_verifie', 'is_active', 'date_inscription',
                  'derniere_connexion_app', 'nb_cotisations', 'nb_transactions']

    def get_nb_cotisations(self, obj):
        return obj.cotisations_creees.count()

    def get_nb_transactions(self, obj):
        return obj.transactions.count()


class AdminVerificationSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_nom = serializers.SerializerMethodField()

    class Meta:
        model = VerificationIdentite
        fields = ['id', 'user', 'user_email', 'user_nom', 'type_document',
                  'photo_recto', 'photo_verso', 'liveness_valide',
                  'statut', 'note_admin', 'date_soumission', 'date_traitement',
                  'paiement_effectue']

    def get_user_email(self, obj):
        return obj.user.email

    def get_user_nom(self, obj):
        return f'{obj.user.prenom} {obj.user.nom}'


class AdminCotisationSerializer(serializers.ModelSerializer):
    createur_email = serializers.SerializerMethodField()

    class Meta:
        model = Cotisation
        fields = ['id', 'nom', 'montant_unitaire', 'nombre_participants',
                  'participants_payes', 'montant_collecte', 'statut',
                  'slug', 'date_creation', 'date_expiration', 'createur_email']

    def get_createur_email(self, obj):
        return obj.createur.email


class AdminTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'user_email', 'type_transaction', 'source',
                  'montant', 'frais_kotizo', 'montant_net', 'statut',
                  'operateur', 'date_creation', 'date_completion']

    def get_user_email(self, obj):
        return obj.user.email


class AdminSanctionSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Sanction
        fields = ['id', 'user', 'user_email', 'niveau', 'raison',
                  'date_debut', 'date_fin', 'active', 'contestee']

    def get_user_email(self, obj):
        return obj.user.email


class AdminAlerteFraudeSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AlerteFraude
        fields = ['id', 'user', 'user_email', 'type_alerte',
                  'description', 'statut', 'data', 'date_creation']

    def get_user_email(self, obj):
        return obj.user.email


class AdminTicketSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = TicketSupport
        fields = ['id', 'user', 'user_email', 'sujet', 'description',
                  'statut', 'priorite', 'cree_par_ia', 'note_admin',
                  'date_creation', 'date_resolution']

    def get_user_email(self, obj):
        return obj.user.email