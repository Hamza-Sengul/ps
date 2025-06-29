from django.contrib import admin
from .models import Table, Pricing, Product, Session, SessionItem

admin.site.register(Table)
admin.site.register(Pricing)
admin.site.register(Product)
admin.site.register(Session)
admin.site.register(SessionItem)