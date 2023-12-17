import random
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
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserProfile
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['GET'], detail=False)
    def random_users(self, request):
        current_user = User.objects.get(id=request.user.id)
        Users = User.objects.filter(
                userprofile__nickname__isnull=False,
            ).exclude(
                id=current_user.id,
            ).exclude(
                id__in=current_user.following_friendship_set.values_list('to_user_id')
            )
        total_users = Users.count()
        if total_users <= 3:
            users = Users
        else:
            random_indices = random.sample(range(total_users), 3)
            users = [Users[index] for index in random_indices]

        serializer = UserSerializerWithProfile(users, many=True)
        return Response(serializer.data)


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
        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
            "access": str(refresh.access_token),
        })

    @action(methods=['Post'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
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
