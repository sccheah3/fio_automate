from django.contrib import admin
from .models import DriveBenchmark, DrivePerformance, BlockPerformance


class DrivePerformanceInline(admin.TabularInline):
    model = DrivePerformance
    extra = 3

class BlockPerformanceInline(admin.TabularInline):
    model = BlockPerformance
    extra = 3

class DriveAdmin(admin.ModelAdmin):
    fields = ['drive_pn', 'drive_fw']
    inlines = [DrivePerformanceInline]
    list_display = ('drive_pn', 'drive_fw')

class DrivePerformanceAdmin(admin.ModelAdmin):
    fields = ['']


admin.site.register(DriveBenchmark, DriveAdmin)