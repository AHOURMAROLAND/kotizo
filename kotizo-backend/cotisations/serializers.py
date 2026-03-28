from django.utils import timezone
from rest_framework import serializers
from .models import Cotisation, Participation, Commentaire, NotationCreateur
from users.serializers import UserPublicSerializer
from core.utils import (
    generer_slug_cotisation,
    generer_code_participation,
    calculer_frais_kotizo,
    calculer_total_participant,
    generer_qr_token,
)


class CotisationCreerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cotisation
        fields = [
            'nom', 'description', 'montant_unitaire',
            'nombre_participants', 'nb_jours',
            'numero_receveur', 'prix_modifiable',
        ]

    def validate_montant_unitaire(self, value):
        if value < 200 or value > 250000:
            raise serializers.ValidationError("Montant entre 200 et 250 000 FCFA.")
        return value

    def validate_nombre_participants(self, value):
        if value < 2:
            raise serializers.ValidationError("Minimum 2 participants.")
        return value

    def validate_nb_jours(self, value):
        if value not in [3, 7, 14, 21, 30]:
            raise serializers.ValidationError("Duree : 3, 7, 14, 21 ou 30 jours.")
        return value

    def validate_numero_receveur(self, value):
        if not value.startswith('+228') or len(value) != 12:
            raise serializers.ValidationError("Format : +228XXXXXXXX")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        slug = generer_slug_cotisation()
        while Cotisation.objects.filter(slug=slug).exists():
            slug = generer_slug_cotisation()

        date_expiration = timezone.now() + timezone.timedelta(
            days=validated_data['nb_jours']
        )

        qr_data = {
            'type': 'cotisation',
            'slug': slug,
            'createur_id': str(user.id),
        }
        qr_token = generer_qr_token(qr_data)

        cotisation = Cotisation.objects.create(
            createur=user,
            slug=slug,
            deep_link=f"kotizo.app/c/{slug}",
            qr_token=qr_token,
            date_expiration=date_expiration,
            **validated_data
        )
        return cotisation


class CotisationListSerializer(serializers.ModelSerializer):
    progression = serializers.SerializerMethodField()
    createur_pseudo = serializers.CharField(source='createur.pseudo')
    createur_verifie = serializers.BooleanField(source='createur.identite_verifiee')

    class Meta:
        model = Cotisation
        fields = [
            'id', 'slug', 'nom', 'description',
            'montant_unitaire', 'nombre_participants',
            'participants_payes', 'montant_collecte',
            'statut', 'progression', 'date_creation',
            'date_expiration', 'deep_link', 'prix_modifiable',
            'createur_pseudo', 'createur_verifie',
        ]

    def get_progression(self, obj):
        return obj.progression()


class CotisationDetailSerializer(serializers.ModelSerializer):
    progression = serializers.SerializerMethodField()
    createur = UserPublicSerializer()
    participations = serializers.SerializerMethodField()
    frais_kotizo = serializers.SerializerMethodField()
    total_si_complet = serializers.SerializerMethodField()
    nb_notes = serializers.SerializerMethodField()

    class Meta:
        model = Cotisation
        fields = [
            'id', 'slug', 'nom', 'description',
            'montant_unitaire', 'nombre_participants',
            'participants_payes', 'montant_collecte',
            'statut', 'progression', 'date_creation',
            'date_expiration', 'deep_link', 'qr_token',
            'prix_modifiable', 'numero_receveur',
            'createur', 'participations',
            'frais_kotizo', 'total_si_complet',
            'peut_etre_supprimee', 'nb_notes',
        ]

    def get_progression(self, obj):
        return obj.progression()

    def get_participations(self, obj):
        parts = obj.participations.filter(
            statut='paye', supprime=False
        ).order_by('rang_paiement')
        return ParticipationSerializer(parts, many=True).data

    def get_frais_kotizo(self, obj):
        return float(calculer_frais_kotizo(obj.montant_unitaire))

    def get_total_si_complet(self, obj):
        return float(obj.montant_unitaire * obj.nombre_participants)

    def get_peut_etre_supprimee(self, obj):
        return obj.peut_etre_supprimee()

    def get_nb_notes(self, obj):
        return obj.notations.count()


class RejoindreSerializer(serializers.Serializer):
    nb_unites = serializers.IntegerField(min_value=1)
    montant_par_unite = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False
    )

    def validate(self, data):
        cotisation = self.context['cotisation']
        nb_unites = data['nb_unites']
        montant_par_unite = data.get('montant_par_unite', cotisation.montant_unitaire)

        if not cotisation.prix_modifiable:
            montant_par_unite = cotisation.montant_unitaire

        if montant_par_unite < cotisation.montant_unitaire:
            raise serializers.ValidationError(
                f"Montant minimum : {cotisation.montant_unitaire} FCFA par unite."
            )

        total = nb_unites * montant_par_unite
        if total > 25000:
            raise serializers.ValidationError(
                "Total maximum par participant : 25 000 FCFA."
            )

        data['montant_par_unite'] = montant_par_unite
        data['montant_total'] = total
        return data


class ParticipationSerializer(serializers.ModelSerializer):
    participant_pseudo = serializers.CharField(source='participant.pseudo')
    participant_nom = serializers.SerializerMethodField()
    participant_verifie = serializers.BooleanField(source='participant.identite_verifiee')

    class Meta:
        model = Participation
        fields = [
            'id', 'participation_id', 'participant_pseudo',
            'participant_nom', 'participant_verifie',
            'montant', 'nb_unites', 'montant_par_unite',
            'statut', 'rang_paiement', 'date_participation',
            'qr_token',
        ]

    def get_participant_nom(self, obj):
        if obj.participant.identite_verifiee:
            return f"{obj.participant.prenom} {obj.participant.nom}"
        return None


class CommentaireSerializer(serializers.ModelSerializer):
    auteur_pseudo = serializers.CharField(source='auteur.pseudo', read_only=True)

    class Meta:
        model = Commentaire
        fields = [
            'id', 'auteur_pseudo', 'message',
            'reponse_admin', 'date_creation', 'date_reponse',
        ]
        read_only_fields = ['reponse_admin', 'date_reponse']

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message trop court (min 10 chars).")
        return value


class NotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotationCreateur
        fields = ['note', 'commentaire']

    def validate_note(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Note entre 1 et 5.")
        return value

    def validate_commentaire(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Commentaire trop court (min 10 chars).")
        return value
