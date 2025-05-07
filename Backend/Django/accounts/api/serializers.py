from datetime import datetime
from django.contrib.auth.models import User
from django.forms import ValidationError
from rest_framework import serializers, exceptions

from accounts.models import UserProfile
from friendships.models import Friendship


class UserSerializer(serializers.ModelSerializer):
    expo_push_token = serializers.CharField(source='profile.expo_push_token')
    class Meta:
        model = User
        fields = ['id', 'username','expo_push_token']


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
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()
    birthday = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], default='male')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'birthday', 'gender')

    # will be called when is_valid
    def validate(self, data):
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
        dob_str = data.get('birthday')
        if dob_str:
            try:
                # Validate format and convert to datetime
                datetime.strptime(dob_str, "%Y/%m/%d")
            except ValueError:
                raise exceptions.ValidationError({
                    'birthday': 'Date of Birth must be in YYYY/MM/DD format.'
                })

        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']
        dob_str = validated_data.get('birthday')
        gender = validated_data.get('gender', 'male')

        # Convert birthday string to datetime.date object
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y/%m/%d").date()
            except ValueError:
                raise exceptions.ValidationError({
                    'birthday': 'Invalid Date of Birth format.'
                })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        #Create UserProfile object
        UserProfile.objects.create(
            user=user,
            dob=dob,
            gender=gender,
        )
        return user
    
class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar', 'dob', 'gender')


class UserProfileSerializerForPushTokenUpdate(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('expo_push_token',)

    def update(self, obj, validated_data):
        # Again, ensure the field name is consistent
        obj.expo_push_token = validated_data.get('expo_push_token', obj.expo_push_token)
        obj.save()
        return obj
