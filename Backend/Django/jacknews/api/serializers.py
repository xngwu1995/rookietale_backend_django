from rest_framework import serializers
from jacknews.models import JackNews


class JackNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JackNews
        fields = ['id', 'title', 'summary', 'content', 'created']
