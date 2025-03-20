from rest_framework.permissions import BasePermission
from django.core.cache import cache


class HasValidCeleryAuth(BasePermission):
    """ Custom permission to check if the request has a valid GUID from the Celery worker. """

    def has_permission(self, request, view):
        guid = request.headers.get("X-GUID")
        if not guid:
            print("No GUID in request headers")
            return False
        print(f"Received GUID: {guid}")
        if cache.get(guid) is None:
            print(f"Invalid or expired GUID: {guid}")
            return False
        return True
