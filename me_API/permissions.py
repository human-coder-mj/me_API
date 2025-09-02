from rest_framework.permissions import IsAdminUser
class IsAdminUserOrReadOnly(IsAdminUser):
    """
    Custom permission class: Only admin users can create/update/delete.
    Anyone can read (GET requests are allowed for everyone).
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # For write permissions, only allow admin users
        return super().has_permission(request, view)