from rest_framework import viewsets

from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFioLog
from . import chart_fio

import io


def upload_fio_log(request):
    if request.method == 'POST':
        form = UploadFioLog(request.POST, request.FILES)
        if form.is_valid():
            output = io.BytesIO()
            chart_fio.chart(request.FILES['file'].read().decode(), output)
            output.seek(0)

            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="drive_performance_chart.xlsx"'
            return response
    else:
        form = UploadFioLog()
    return render(request, 'fio_chart/upload.html', {'form': form})

def automate_fio_test_and_chart(request):


#class DriveViewSet(viewsets.ModelViewSet):
#    queryset = DriveBenchmark.objects.all()
#    serializer_class = DriveSerializer

#class PerformanceViewSet(viewsets.ModelViewSet):
#    queryset = Performance.objects.all()
#    serializer_class = PerformanceSerializer