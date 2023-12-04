from rest_framework import serializers
from chatgpt.models import ChatGPTInteraction

class ChatGPTInteractionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChatGPTInteraction
        fields = ['id', 'user', 'requirement_text', 'content_text', 'response_text', 'request_time', 'response_time']
        read_only_fields = ['id', 'user', 'request_time', 'response_time']

    def create(self, validated_data):
        # Custom method to create a new ChatGPTInteraction instance
        return ChatGPTInteraction.objects.create(**validated_data)
