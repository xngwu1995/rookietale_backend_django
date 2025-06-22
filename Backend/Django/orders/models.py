from django.db.models.signals import pre_delete
from django.db import models
from django.dispatch import receiver

class Session(models.Model):
    DRAFT, OPEN, CLOSED = "DRAFT", "OPEN", "CLOSED"
    STATUS = [(DRAFT, "Draft"), (OPEN, "Open"), (CLOSED, "Closed")]

    title = models.CharField(max_length=120)
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    status = models.CharField(max_length=6, choices=STATUS, default=DRAFT)
    note = models.TextField(blank=True)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    # category choices
    BREAD, FILLING_TOAST, LYE, LYE_STICK, LYE_BALL, BG = (
        "大吐司",
        "小吐司",
        "司康",
        "碱水棒",
        "碱水球",
        "贝果",
    )
    CATEGORY = [
        (BREAD, "大吐司"),
        (FILLING_TOAST, "小吐司"),
        (LYE, "司康"),
        (LYE_STICK, "碱水棒"),
        (LYE_BALL, "碱水球"),
        (BG, "贝果"),
    ]

    category     = models.CharField(max_length=20, choices=CATEGORY, default=BREAD)
    name         = models.CharField(max_length=120)
    base_price   = models.DecimalField(max_digits=6, decimal_places=2)
    description  = models.TextField(blank=True)
    image  = models.CharField(max_length=120, blank=True)   # filename only

    def __str__(self):
        return f"{self.category} - {self.name}"


# orders/models.py
class SessionItem(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_items")
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    price_override = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    stock = models.PositiveSmallIntegerField(default=10)   # how many you will bake
    sold  = models.PositiveSmallIntegerField(default=0)     # auto-increment on each order

    @property
    def price(self):
        return self.price_override or self.item.base_price

    @property
    def remaining(self):
        return self.stock - self.sold



class Order(models.Model):
    PENDING, PAID, FULFILLED, CANCELLED = "PEND", "PAID", "FULL", "CANC"
    STATUS = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (FULFILLED, "Fulfilled"),
        (CANCELLED, "Cancelled"),
    ]

    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    wechat_id = models.CharField(max_length=80)
    address = models.TextField(blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=4, choices=STATUS, default=PENDING)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    grand_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"#{self.id} {self.wechat_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    qty = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)


@receiver(pre_delete, sender=Order)
def restock_when_order_deleted(sender, instance, **kwargs):
    if instance.session.status != Session.OPEN:
        return
    for oi in instance.items.all():
        SessionItem.objects.filter(
            session=instance.session,
            item=oi.item,
        ).update(
            sold=models.Case(
                models.When(sold__gte=oi.qty,
                            then=models.F("sold") - oi.qty),
                default=0,
                output_field=models.PositiveSmallIntegerField(),
            )
        )
