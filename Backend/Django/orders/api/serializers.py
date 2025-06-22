from rest_framework import serializers
from ..models import Session, SessionItem, MenuItem, Order, OrderItem
from django.db import transaction, models


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "name",  "category", "description", "base_price", "image")


class SessionItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()

    class Meta:
        model = SessionItem
        fields = ("item", "price")


class SessionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ("id", "status", "opens_at", "closes_at", "items")

    # orders/serializers.py  – tweak the helper that builds items
    def get_items(self, obj):
        qs = obj.session_items.select_related("item")
        return [
            {
                "id": si.item.id,
                "name": si.item.name,
                "price": si.price,
                "image": si.item.image,
                "category": si.item.category,
                "description": si.item.description,
                "remaining": si.remaining,  # 👈 send remaining stock
            }
            for si in qs
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    wechat_id = serializers.CharField(max_length=80)
    address = serializers.CharField(max_length=255)
    notes = serializers.CharField(max_length=255)
    items = OrderItemCreateSerializer(many=True)

    def validate(self, data):
        session = Session.objects.get(id=data["session_id"], status=Session.OPEN)
        items_parsed, subtotal = [], 0

        with transaction.atomic():
            for entry in data["items"]:
                si = (
                    SessionItem.objects
                    .select_for_update()                 # lock row
                    .get(session=session, item_id=entry["id"])
                )
                if entry["qty"] > si.remaining:
                    raise serializers.ValidationError(
                        {"detail": f"{si.item.name} 只剩 {si.remaining} 份"}
                    )

                price = si.price
                total = price * entry["qty"]
                items_parsed.append((si, entry["qty"], price, total))
                subtotal += total

        data.update(session=session, items_parsed=items_parsed, subtotal=subtotal)
        return data

    def create(self, validated):
        with transaction.atomic():
            order = Order.objects.create(
                session     = validated["session"],
                wechat_id   = validated["wechat_id"],
                address      = validated["address"],
                notes      = validated["notes"],
                subtotal    = validated["subtotal"],
                grand_total = validated["subtotal"],
            )

            for si, qty, price, total in validated["items_parsed"]:
                OrderItem.objects.create(
                    order       = order,
                    item        = si.item,
                    qty         = qty,
                    unit_price  = price,
                    total_price = total,
                )
                # increment sold counter
                si.sold = models.F("sold") + qty
                si.save(update_fields=["sold"])        # avoids race duplicates

        return order
