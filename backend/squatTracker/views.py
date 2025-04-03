from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from .serializers import SquatAnalysisSerializer
from .squat_analysis import analyze_squat_video
from .models import SquatAnalysis


class SquatAnalysisView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        video = request.FILES.get('video')
        if not video:
            return Response({'error': 'No video uploaded'}, status=400)

        # Save video to media folder
        save_path = os.path.join(settings.MEDIA_ROOT, video.name)
        with open(save_path, 'wb+') as f:
            for chunk in video.chunks():
                f.write(chunk)

        # Run squat analysis
        try:
            result = analyze_squat_video(save_path)
            return Response(result, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AllSquatsView(APIView):
    def get(self, request):
        squats = SquatAnalysis.objects.all().order_by('rep')
        serializer = SquatAnalysisSerializer(squats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
