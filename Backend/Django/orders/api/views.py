from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, mixins, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Session, Order, MenuItem, OrderItem
from orders.api.serializers import SessionSerializer, OrderCreateSerializer, MenuItemSerializer


@method_decorator(cache_page(60 * 24), name="list")
class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.exclude(category='大吐司').exclude(image='').order_by("category", "name")
    serializer_class   = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    pagination_class = None 


# ── order-item nested ────────────────────────────────────────────────
class MenuItemSlimSer(serializers.ModelSerializer):
    class Meta:
        model  = MenuItem
        fields = ("id", "name", "image", "category")   # only the front-end needs

class OrderItemNestedSer(serializers.ModelSerializer):
    item = MenuItemSlimSer(read_only=True)   # ← swap in the object, not slug

    class Meta:
        model  = OrderItem
        fields = ("item", "qty", "unit_price", "total_price")


# ── order nested ─────────────────────────────────────────────────────
class OrderNestedSer(serializers.ModelSerializer):
    items = OrderItemNestedSer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = (
            "id", "wechat_id", "address",
            "notes", "subtotal", "grand_total",
            "status", "created_at", "items",
        )


# ── session w/ orders ────────────────────────────────────────────────
class SessionWithOrdersSer(serializers.ModelSerializer):
    orders = OrderNestedSer(source="order_set", many=True, read_only=True)

    class Meta:
        model  = Session
        fields = (
            "id", "status", "opens_at", "closes_at",
            "orders",
        )

# ─── SESSION ──────────────────────────────────────────────────────────
class SessionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    # unchanged top-level attributes…
    queryset = Session.objects.filter(status=Session.OPEN)
    serializer_class = SessionSerializer      # default
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"], url_path="open")
    def open_session(self, request):
        session = (
            Session.objects
            .filter(status=Session.OPEN)
            .prefetch_related(      # quick performance win
                "order_set__items__item"
            )
            .order_by("opens_at")
            .first()
        )

        if not session:
            return Response(
                {
                    "status": "CLOSED",
                    "next_opens_at": None,
                    "items": [],
                },
                status=status.HTTP_200_OK,
            )

        # ➜ if admin asked for orders, give the fat payload
        include_orders = (
            request.query_params.get("include") == "orders"
            and request.user
            and request.user.is_staff
        )

        if include_orders:
            data = SessionWithOrdersSer(session, context={"request": request}).data
        else:
            data = SessionSerializer(session, context={"request": request}).data

        data["status"] = "OPEN"
        return Response(data, status=status.HTTP_200_OK)


# ─── ORDER (CSRF-exempt just for this viewset) ───────────────────────
@method_decorator(csrf_exempt, name="dispatch")
class OrderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.AllowAny]  # anyone may POST

    def get_permissions(self):
        # only admins can list/update orders; create is open
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
