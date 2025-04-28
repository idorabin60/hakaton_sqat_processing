from rest_framework import serializers
from .models import SquatAnalysis
from .models import WorkoutVideo


class SquatAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquatAnalysis
        fields = '__all__'

# serializers.py


class WorkoutVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutVideo
        fields = ['id', 'title', 'video']
