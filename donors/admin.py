from django.contrib import admin
from .models import DonorProfile, BloodRequest
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'city', 'phone', 'is_available')
    list_filter = ('blood_group', 'city', 'is_available')
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'hospital', 'city', 'urgency', 'status', 'created_at')
    list_filter = ('blood_group', 'status', 'urgency')
admin.site.register(DonorProfile, DonorProfileAdmin)
admin.site.register(BloodRequest, BloodRequestAdmin)
