from django.urls import path
from .views import SquatAnalysisView, AllSquatsView

urlpatterns = [
    path('analyze/', SquatAnalysisView.as_view(), name='analyze'),
    path('squats/', AllSquatsView.as_view(), name='squats')
]
