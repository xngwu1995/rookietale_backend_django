from django.contrib.auth.models import User
from rest_framework import serializers, exceptions

from accounts.models import UserProfile
from friendships.models import Friendship


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    avatar = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Friendship.objects.filter(from_user=request.user, to_user=obj).exists()
        return False
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar', 'is_following')


class UserSerializerForTweet(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'User does not exist.'
            })
        return data


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length = 20, min_length = 6)
    password = serializers.CharField(max_length = 20, min_length = 6)
    email = serializers.EmailField()
    inviation = serializers.CharField(max_length = 20, min_length = 1)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'inviation')

    # will be called when is_valid
    def validate(self, data):
        if data['inviation'].lower() != 'xuguang':
            raise exceptions.ValidationError({
                    'inviation': 'This code is not correct.'
                })
        # check not allowed characteristic
        for ch in data['username']:
            if ch in "()%@":
                raise exceptions.ValidationError({
                    'username': 'This username has not allowed characteristic.'
                })
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        #Create UserProfile object
        user.profile
        return user
    
class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')
