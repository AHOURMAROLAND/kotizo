from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings


def require_verified(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not getattr(request.user, 'identite_verifiee', False):
            return Response(
                {'error': 'Verification identite requise pour cette action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return func(self, request, *args, **kwargs)
    return wrapper


def throttle_cotisation(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        niveau = getattr(user, 'niveau', 'basique')
        if niveau == 'business':
            return func(self, request, *args, **kwargs)
        from django.utils import timezone
        from cotisations.models import Cotisation
        aujourd_hui = timezone.now().date()
        nb_jour = Cotisation.objects.filter(
            createur=user,
            date_creation__date=aujourd_hui,
            supprime=False
        ).count()
        limite_jour = 3 if niveau == 'basique' else 20
        if nb_jour >= limite_jour:
            return Response(
                {'error': f'Limite atteinte : {limite_jour} cotisations/jour pour votre niveau.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        if niveau == 'basique':
            il_y_a_7j = timezone.now() - timezone.timedelta(days=7)
            nb_semaine = Cotisation.objects.filter(
                createur=user,
                date_creation__gte=il_y_a_7j,
                supprime=False
            ).count()
            if nb_semaine >= 12:
                return Response(
                    {'error': 'Limite atteinte : 12 cotisations/semaine pour le niveau Basique.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        return func(self, request, *args, **kwargs)
    return wrapper
