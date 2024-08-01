from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
	message = "You do not have permission to access this object"
	'''
	if detail=False action, just test has_permission
	else, it will check has_permission and has_object_permission
	'''
	def has_permission(self, request, view):
		return True

	def has_object_permission(self, request, view, obj):
		return request.user.is_authenticated and request.user == obj.user


class IsAdminUser(BasePermission):
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an admin
        return request.user and request.user.is_authenticated and request.user.is_staff
