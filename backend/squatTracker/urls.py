from django.urls import path
from .views import SquatAnalysisView, AllSquatsView, VideoUploadView, FirstWorkoutVideoView

urlpatterns = [
    path('analyze/', SquatAnalysisView.as_view(), name='analyze'),
    path('squats/', AllSquatsView.as_view(), name='squats'),
    path('upload/', VideoUploadView.as_view(), name='upload'),
    path("first-video/", FirstWorkoutVideoView.as_view(), name="first-video"),


]
