from django.contrib import admin
from .models import Product , Contact , Orders , OrderUpdate
# Register your models here.

admin.site.register(Product)                    # We register our created class in 'models.py' file here

admin.site.register(Contact)

admin.site.register(Orders)

admin.site.register(OrderUpdate)
