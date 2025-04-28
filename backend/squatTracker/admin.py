from django.contrib import admin
from .models import SquatAnalysis, WorkoutVideo
from django.utils.html import format_html


@admin.register(SquatAnalysis)
class SquatAnalysisAdmin(admin.ModelAdmin):
    list_display = ('rep', 'duration_sec', 'min_depth',
                    'valid_depth', 'knees_over_toes', 'back_straight')
    list_filter = ('valid_depth', 'back_straight', 'knees_over_toes')
    search_fields = ('rep',)


@admin.register(WorkoutVideo)
class WorkoutVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'video_preview')
    search_fields = ('title',)
    readonly_fields = ('video_preview',)

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                f'<video width="250" controls>'
                f'<source src="{obj.video.url}" type="video/mp4">'
                f'Your browser does not support the video tag.'
                f'</video>'
            )
        return "No video"
    video_preview.short_description = "Preview"

# Register your models here.
