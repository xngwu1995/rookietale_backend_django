# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Session, MenuItem, SessionItem


# ─── MenuItem ──────────────────────────────────────────────
# orders/admin.py
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ("name", "category", "base_price", "image")
    list_filter   = ("category",)                # ← filter sidebar
    search_fields = ("name",)
    list_per_page = 40


# ─── SessionItem inline (sortable) ─────────────────────────
class SessionItemInline(admin.TabularInline):
    model = SessionItem
    extra = 0
    fields = ("item", "price_override", "position", "stock", "sold")
    readonly_fields = ()
    ordering = ("position",)


# ─── Session ───────────────────────────────────────────────
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "opens_at", "closes_at")
    list_filter = ("status",)
    search_fields = ("title", "note")
    date_hierarchy = "opens_at"
    inlines = (SessionItemInline,)


# ─── OrderItem inline (read-only) ─────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = True
    fields = ("item", "qty", "unit_price", "total_price")
    readonly_fields = ("total_price",)
    show_change_link = False


# ─── custom actions ───────────────────────────────────────
def mark_paid(modeladmin, request, queryset):
    queryset.update(status=Order.PAID)
mark_paid.short_description = "Mark selected orders as Paid"

def mark_fulfilled(modeladmin, request, queryset):
    queryset.update(status=Order.FULFILLED)
mark_fulfilled.short_description = "Mark selected orders as Fulfilled"

def cancel_order(modeladmin, request, queryset):
    queryset.update(status=Order.CANCELLED)
cancel_order.short_description = "Cancel (no refund)"


# ─── Order ────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "wechat_id", "session", "created_at", "address", "notes", "status", "grand_total")
    list_filter = ("status", "session")
    search_fields = ("wechat_id", "customer_name")
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)
    readonly_fields = ("subtotal", "grand_total", "created_at")
    actions = (mark_paid, mark_fulfilled, cancel_order)

