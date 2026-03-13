from rest_framework import serializers
from django.utils import timezone
from .models import Cotisation, Participation, Signalement


class CotisationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotisation
        fields = ['nom', 'description', 'montant_unitaire',
                  'nombre_participants', 'numero_receveur', 'date_expiration']

    def validate_montant_unitaire(self, value):
        if value < 200:
            raise serializers.ValidationError('Montant minimum 200 FCFA')
        if value > 25000:
            raise serializers.ValidationError('Montant maximum 25 000 FCFA')
        return value

    def validate_nombre_participants(self, value):
        if value < 2:
            raise serializers.ValidationError('Minimum 2 participants')
        return value

    def validate_date_expiration(self, value):
        maintenant = timezone.now()
        delta = value - maintenant
        if delta.days > 30:
            raise serializers.ValidationError('Duree maximum 30 jours')
        if value <= maintenant:
            raise serializers.ValidationError('La date doit etre dans le futur')
        return value

    def validate_numero_receveur(self, value):
        numero = value.strip().replace(' ', '')
        if not numero.startswith('+228'):
            if len(numero) == 8:
                numero = '+228' + numero
            else:
                raise serializers.ValidationError('Numero invalide')
        return numero


class CotisationSerializer(serializers.ModelSerializer):
    createur_nom = serializers.SerializerMethodField()
    est_complete = serializers.SerializerMethodField()
    montant_total = serializers.SerializerMethodField()
    progression = serializers.SerializerMethodField()

    class Meta:
        model = Cotisation
        fields = ['id', 'nom', 'description', 'montant_unitaire',
                  'nombre_participants', 'participants_payes',
                  'montant_collecte', 'montant_total', 'progression',
                  'statut', 'slug', 'date_expiration', 'date_creation',
                  'createur_nom', 'est_complete']

    def get_createur_nom(self, obj):
        return f'{obj.createur.prenom} {obj.createur.nom}'

    def get_est_complete(self, obj):
        return obj.is_complete()

    def get_montant_total(self, obj):
        return obj.get_montant_total()

    def get_progression(self, obj):
        if obj.nombre_participants == 0:
            return 0
        return round((obj.participants_payes / obj.nombre_participants) * 100)


class ParticipationSerializer(serializers.ModelSerializer):
    participant_nom = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = ['id', 'participant_nom', 'statut', 'montant',
                  'date_participation', 'date_paiement', 'recu_confirme']

    def get_participant_nom(self, obj):
        return f'{obj.participant.prenom} {obj.participant.nom}'


class SignalementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signalement
        fields = ['raison', 'description']