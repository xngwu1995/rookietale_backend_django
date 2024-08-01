from stocks.models import Stock, StrategyData, TradeRecord
from rest_framework import serializers

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['ticker', 'company', 'sector', 'industry', 'country']


class StrategyStockSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = StrategyData
        fields = ['id', 'stock', 'created_at', 'strategy']


class TradeRecordSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = TradeRecord
        fields = [
            'id',
            'stock',
            'cost',
            'quantity',
            'strategy',
            'reason',
            'created_date',
            'active',
            'sell_reason',
            'sell_price',
            'sell_date',
            'revenue',
            'closed'
        ]
        read_only_fields = ['id', 'revenue', 'closed']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['sellReason'] = ret.pop('sell_reason', None)
        ret['sellPrice'] = ret.pop('sell_price', None)
        ret['sellDate'] = ret.pop('sell_date', None)
        return ret


class TradeRecordSerializerForCreate(serializers.ModelSerializer):
    stock_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = TradeRecord
        fields = [
            'id', 
            'stock_id',
            'user_id',
            'cost', 
            'quantity', 
            'strategy', 
            'reason', 
            'created_date', 
            'active', 
            'sell_reason', 
            'sell_price', 
            'sell_date', 
            'revenue'
        ]
        read_only_fields = ['id', 'revenue']


class TradeRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeRecord
        fields = ['active', 'sell_reason', 'sell_price', 'sell_date']

    def validate(self, data):
        # Ensure at least one field is provided for update
        if not any(data.values()):
            raise serializers.ValidationError("At least one field (sell_reason, sell_price, or sell_date) must be provided for update.")
        return data
