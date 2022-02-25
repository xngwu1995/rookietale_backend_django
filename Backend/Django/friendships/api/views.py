from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # I would like to POST /api/friendship/1/follow will follow user whose user_id=1
    # Thus queryset need to be User.objects.all()
    # If I use Friendship.objects.all, it will result in 404 Not Found
    # because detail=True in actions, it will use get_object() first
    # queryset.filter(pk=1) will check the object
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers
        friendship = Friendship.objects.filter(to_user_id=pk)
        serializer = FollowerSerializer(friendship, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # GET /api/friendships/1/followers
        friendship = Friendship.objects.filter(from_user_id=pk)
        serializer = FollowingSerializer(friendship, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        follower_user = self.get_object()
        # if duplicate request
        # use silent processing
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': follower_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollower_user = self.get_object()
        if request.user.id == unfollower_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        '''
        delete at queryset will return two values, one is how many data are deleted,
        the second one is how many data deleted in a specific type.
        Foreign key set cascade. We should avoid the cascade. Thus, we need to use
        on_delete=models.SET_NULL
        '''
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollower_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message': 'this is friendships'})