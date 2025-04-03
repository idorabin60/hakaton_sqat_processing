from django.contrib import admin
from .models import SquatAnalysis


@admin.register(SquatAnalysis)
class SquatAnalysisAdmin(admin.ModelAdmin):
    list_display = ('rep', 'duration_sec', 'min_depth',
                    'valid_depth', 'knees_over_toes', 'back_straight')
    list_filter = ('valid_depth', 'back_straight', 'knees_over_toes')
    search_fields = ('rep',)

# Register your models here.
