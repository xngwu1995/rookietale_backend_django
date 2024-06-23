from collections import OrderedDict
from LMT.models import LMT, Stock
from rest_framework import serializers


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['symbol', 'current_price', 'rank', 'analysis', 'instructors', 'updated_at', 'gpt_updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(representation, OrderedDict):
            representation = dict(representation)
        return representation


class LMTSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=5)
    cost = serializers.DecimalField(max_digits=10, decimal_places=5)
    stock = StockSerializer(read_only=True)
    net_worth = serializers.SerializerMethodField()

    class Meta:
        model = LMT
        fields = ('id', 'user_id', 'quantity', 'cost', 'stock', 'net_worth')

    def get_net_worth(self, obj):
        return (obj.stock.current_price - obj.cost) * obj.quantity


class LMTSerializerForCreate(LMTSerializer):
    symbol = serializers.CharField(max_length=80)

    class Meta(LMTSerializer.Meta):
        fields = LMTSerializer.Meta.fields + ('symbol',)

    def create(self, validated_data):
        user_id = validated_data['user_id']
        symbol = validated_data['symbol']
        stock = Stock.get_or_create(symbol)
        quantity = validated_data['quantity']
        cost = validated_data['cost']
        return LMT.objects.create(
            user_id=user_id,
            stock_id=stock.id,
            quantity=quantity,
            cost=cost
        )