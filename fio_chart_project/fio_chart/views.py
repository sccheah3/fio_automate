from rest_framework import viewsets

from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFioLogForm, AutomateFioForm
from . import chart_fio

import io
import subprocess
import time

RC_URL = '172.16.118.50/fio_automate_staging.sh'


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
		form = UploadFioLogForm()
	return render(request, 'fio_chart/upload.html', {'form': form})

def automate_fio_test_and_chart(request):
	if request.method == 'POST':
		form = AutomateFioForm(request.POST)

		if form.is_valid():
			set_autopxe(form.cleaned_data['lan_mac'], form.cleaned_data['cburn_img'], form.cleaned_data['burnin_dir'])
			reset_server(form.cleaned_data['bmc_ip'], form.cleaned_data['bmc_username'], form.cleaned_data['bmc_password'])
			return HttpResponse('submitted')

	form = AutomateFioForm()
	return render(request, 'fio_chart/automate_drive_benchmark_form.html', {'form': form})


# can try to convert this to pycurl later. currently creating subproc with curl cmd
def set_autopxe(lan_mac, cburn_img, burnin_dir):
	command = "%s %s %s" %(cburn_img, RC_URL, burnin_dir)
	subprocess.Popen(['curl', '-X', 'POST', '-F', 'command=%s'%(command), '-F', 'address=%s'%(lan_mac), '-F', 'action=Update', \
					'172.16.0.3/cgi-bin/autopxe.php'])

# dont want to do reset because when system is initial off state, will not turn on
def reset_server(bmc_ip, bmc_username, bmc_password):
	subprocess.Popen(['ipmitool', '-U', bmc_username, '-P', bmc_password, '-H', 'bmc_ip', 'power', 'off'])
	time.sleep(10)
	subprocess.Popen(['ipmitool', '-U', bmc_username, '-P', bmc_password, '-H', 'bmc_ip', 'power', 'on'])

#class DriveViewSet(viewsets.ModelViewSet):
#    queryset = DriveBenchmark.objects.all()
#    serializer_class = DriveSerializer

#class PerformanceViewSet(viewsets.ModelViewSet):
#    queryset = Performance.objects.all()
#    serializer_class = PerformanceSerializer
