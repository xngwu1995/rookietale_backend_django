from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from taskmanager.models import TaskManager
from friendships.services import FriendshipService

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
        return TaskManager.objects.create(
            mistress=self.mistress,
            sub_id=sub_id,
            name=name,
        )

    def update(self, obj, validated_data):
        obj.sub_id = validated_data.get('sub_id', obj.sub_id)
        obj.name = validated_data.get('name', obj.name)
        obj.save()
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
        return obj