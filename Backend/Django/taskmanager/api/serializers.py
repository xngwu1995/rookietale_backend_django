from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from taskmanager.models import TaskManager
from friendships.services import FriendshipService
from accounts.models import UserProfile
from utils.push_notification import send_push_notification


class TaskManagerSerializer(serializers.ModelSerializer):
    sub_id = serializers.IntegerField()
    mistress_username = serializers.CharField(source='mistress.username', read_only=True)
    sub_username = serializers.CharField(source='sub.username', read_only=True)

    class Meta:
        model = TaskManager
        fields = ('sub_id', 'mistress_username', 'sub_username', 'name')

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if it exists
        self.mistress = kwargs.pop('mistress', None)
        super(TaskManagerSerializer, self).__init__(*args, **kwargs)

    def validate(self, attrs):
        sub_id = attrs['sub_id']
        if not FriendshipService.has_followed(self.mistress.id, sub_id):
            raise ValidationError({
                'message': 'You need to follow the user first'
            })
        if not FriendshipService.has_following(self.mistress.id, sub_id):
            raise ValidationError({
                'message': 'The user need to follow you before received the task'
            })
        return attrs

    def create(self, validated_data):
        sub_id = validated_data['sub_id']
        name = validated_data['name']
        task_manager = TaskManager.objects.create(
            mistress=self.mistress,
            sub_id=sub_id,
            name=name,
        )
        if sub_id == self.mistress.id:
            return task_manager
        try:
            user_profile = UserProfile.objects.get(user_id=sub_id)
            # Customize your notification title and body as needed
            if token := user_profile.expo_push_token:
                send_push_notification(
                    user_profile=user_profile,
                    token=token,
                    title="New Task Assigned",
                    body=f"You have a new task from {self.mistress.username}"
                )
        except UserProfile.DoesNotExist:
            raise
        return task_manager

    def update(self, obj, validated_data):
        sub_id = validated_data.get('sub_id', obj.sub_id)
        obj.sub_id = sub_id
        obj.name = validated_data.get('name', obj.name)
        obj.save()
        if sub_id == self.mistress.id:
            return obj
        try:
            user_profile = UserProfile.objects.get(user_id=obj.sub_id)
            # Customize your notification title and body as needed
            if token := user_profile.expo_push_token:
                send_push_notification(
                    user_profile=user_profile,
                    token=token,
                    title="Task Updated",
                    body=f"You have an updated task from {self.mistress.username}"
                )
        except UserProfile.DoesNotExist:
            raise
        return obj


class TaskManagerSerializerForGet(TaskManagerSerializer):
    class Meta:
        model = TaskManager
        fields = ('id', 'sub_id', 'mistress_id', 'mistress_username', 'sub_username', 'name', 'completed')


class TaskManagerCompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskManager
        fields = ('completed',)

    def update(self, obj, validated_data):
        obj.completed = validated_data.get('completed', obj.completed)
        obj.save()
        if obj.sub_id == obj.mistress_id:
            return obj
        try:
            user_profile = UserProfile.objects.get(user_id=obj.mistress_id)
            # Customize your notification title and body as needed
            if token := user_profile.expo_push_token:
                completed_status = 'completed'
                if not obj.completed:
                    completed_status = 'uncompleted'
                send_push_notification(
                    user_profile=user_profile,
                    token=token,
                    title="Task Updated",
                    body=f"Your lover {obj.sub.username} {completed_status} the task for you!"
                )
        except UserProfile.DoesNotExist:
            raise
        return obj


class TaskManagerSendReminderSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskManager
        fields = ('sub_id',)

    def update(self, obj, validated_data):
        if obj.sub_id == obj.mistress_id:
            return obj
        try:
            user_profile = UserProfile.objects.get(user_id=obj.sub_id)
            if token := user_profile.expo_push_token:
                send_push_notification(
                    user_profile=user_profile,
                    token=token,
                    title="Task Reminder",
                    body=f"Your lover {obj.mistress.username} reminder you to completed the task: {obj.name} asap!"
                )
        except UserProfile.DoesNotExist:
            raise
        return obj