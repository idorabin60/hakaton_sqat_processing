from rest_framework import serializers
from .models import SquatAnalysis


class SquatAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquatAnalysis
        fields = '__all__'
