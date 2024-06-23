from django.contrib import admin

# Register your models here.
from .models import LMT, Stock

admin.site.register(Stock)
admin.site.register(LMT)