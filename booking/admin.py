from django.contrib import admin
from .models import LocationForApartment, Owner, region, UserProfile # Corrected model names
# Register your models here.
class apratments_list(admin.ModelAdmin):
    readonly_fields = ("title",)
admin.site.register(LocationForApartment ,apratments_list) # Corrected model name
admin.site.register(Owner) # Corrected model name
admin.site.register(UserProfile)
admin.site.register(region)
