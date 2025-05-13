from django.contrib import admin
from .models import Settings

# Register your models here.
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'value', 'category')
    search_fields = ('name', 'code', 'category')
    list_filter = ('category',)
    ordering = ('category', 'name')


admin.site.register(Settings, SettingsAdmin)