from rest_framework import serializers
from fio_chart_project.fio_chart.models import DriveBenchmark, Performance

class DriveSerializer(serializers.HyperlinkedModelSerializer):
    performances = serializers.PrimaryKeyRelatedField(many=True, queryset=Performance.objects.all())
    class Meta:
        model = DriveBenchmark
        fields = ['url', 'id', 'drive_name', 'performances']

class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ['pk', 'drive', 'block_size', 'read_speed', 'write_speed']