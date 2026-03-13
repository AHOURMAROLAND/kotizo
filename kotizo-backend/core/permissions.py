from rest_framework.permissions import BasePermission


class IsVerifie(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.niveau in ['verifie', 'business']


class IsBusiness(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.niveau == 'business'


class IsAdminKotizo(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff