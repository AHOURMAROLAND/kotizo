from rest_framework.permissions import BasePermission


class IsAdminKotizo(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and
            getattr(request.user, 'admin_role', None) == 'super_admin'
        )


class HasStaffPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_staff:
            return False
        if getattr(request.user, 'admin_role', None) == 'super_admin':
            return True
        section = getattr(view, 'required_section', None)
        level = getattr(view, 'required_level', 'read')
        if not section:
            return False
        try:
            from admin_panel.models import StaffPermission
            perm = StaffPermission.objects.filter(
                staff_user=request.user,
                section=section,
                actif=True
            ).first()
            if not perm:
                return False
            levels = {'read': 1, 'write': 2, 'full': 3}
            return levels.get(perm.permission_level, 0) >= levels.get(level, 1)
        except Exception:
            return False


class IsVerified(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'identite_verifiee', False)
        )
