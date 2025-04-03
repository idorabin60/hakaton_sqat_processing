from django.urls import path
from .views import SquatAnalysisView

urlpatterns = [
    path('analyze/', SquatAnalysisView.as_view(), name='analyze'),
]
