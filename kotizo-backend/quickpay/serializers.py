from rest_framework import serializers
from .models import QuickPay


class QuickPayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickPay
        fields = ['montant', 'description', 'numero_receveur']

    def validate_montant(self, value):
        if value < 200:
            raise serializers.ValidationError('Montant minimum 200 FCFA')
        if value > 25000:
            raise serializers.ValidationError('Montant maximum 25 000 FCFA')
        return value

    def validate_numero_receveur(self, value):
        numero = value.strip().replace(' ', '')
        if not numero.startswith('+228'):
            if len(numero) == 8:
                numero = '+228' + numero
            else:
                raise serializers.ValidationError('Numero invalide')
        return numero


class QuickPaySerializer(serializers.ModelSerializer):
    createur_nom = serializers.SerializerMethodField()
    est_expire = serializers.SerializerMethodField()

    class Meta:
        model = QuickPay
        fields = ['id', 'code', 'montant', 'description',
                  'statut', 'date_creation', 'date_expiration',
                  'date_paiement', 'createur_nom', 'est_expire']

    def get_createur_nom(self, obj):
        return f'{obj.createur.prenom} {obj.createur.nom}'

    def get_est_expire(self, obj):
        from django.utils import timezone
        return obj.date_expiration <= timezone.now()