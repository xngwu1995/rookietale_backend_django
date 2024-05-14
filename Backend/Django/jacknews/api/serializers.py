from rest_framework import serializers
from jacknews.models import JackNews


class JackNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JackNews
        fields = ['id', 'title', 'summary', 'content', 'created']

class StockSignalSerializer(serializers.ModelSerializer):
    stocksymbol = serializers.CharField()

    class Meta:
        model = JackNews
        fields = ('stocksymbol',)