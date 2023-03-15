from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserProfileSerializerForUpdate,
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
    UserSerializerWithProfile,
)
from django.contrib.auth import (
    logout as django_logout,
    authenticate as django_authenticate,
    login as django_login,
)
from rest_framework.permissions import AllowAny

from accounts.models import UserProfile
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAuthenticated,)


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['Get'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)


    @action(methods=['Post'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['Post'], detail=False)
    def login(self, request):
        # get username and password from request
        serializer = LoginSerializer(data = request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status = 400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = django_authenticate(username = username, password = password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'Username and password does not match.',
            }, status=400)
        # login
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['Post'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data = request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status = 400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status = 201)

class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate
