from rest_framework import viewsets

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .forms import UploadFioLogForm, AutomateFioForm, SavePerformanceForm
from .models import DriveBenchmark, DrivePerformance, BlockPerformance
from . import chart_fio
from . import utilities

import io
import subprocess
import time

RC_URL = '172.16.118.50/fio_automate_staging.sh'

def view_drives(request):
	drives = DriveBenchmark.objects.all()
	template = loader.get_template('fio_chart/drives.html')
	context = {'drives': drives}

	return HttpResponse(template.render(context, request))


def performance_comparison(request):
	drive_names = []

	# get form names we want from POST
	for key in request.POST:
		if key.startswith("drive_name"):
			drive_names.append(key)

	drives = []
	# query DB to get list of drives to compare
	print (drive_names)
	for key in drive_names:
		drives.append(DriveBenchmark.objects.get(pk=request.POST.get(key)))
	
	return render(request, 'fio_chart/performance_comparison.html', {'drives': drives})


def drive_detail(request, drive_id):
	drive = DriveBenchmark.objects.get(id=drive_id)
	template = loader.get_template('fio_chart/drive_detail.html')
	context = {'drive': drive, 'avg': drive.get_avg}

	return HttpResponse(template.render(context, request))


# handles fio log file upload. charts/graphs and client downloads xlsx file
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

# deals with cburn automation for saving disk data and bench performance
# for database
def parse_and_save_performance(request):
	if request.method == 'POST':
		form = SavePerformanceForm(request.POST, request.FILES)
		if form.is_valid():
			fio_log_file = request.FILES['fio_log_file']
			drive_info_file = request.FILES['drive_info_file']

			utilities.parse_and_save(drive_info_file, fio_log_file)

			return HttpResponse("Submitted. Check the logs.")
	else:
		form = SavePerformanceForm()

	return render(request, 'fio_chart/upload_performance_data.html', {'form': form})



# handles form for system info and commands to begin automation test
def automate_fio_test_and_chart(request):
	if request.method == 'POST':
		form = AutomateFioForm(request.POST)

		if form.is_valid():
			print(form.cleaned_data)
			set_autopxe(form.cleaned_data['lan_mac'], form.cleaned_data['cburn_img'], form.cleaned_data['burnin_dir'])
			reset_server(form.cleaned_data['bmc_ip'], form.cleaned_data['bmc_username'], form.cleaned_data['bmc_password'])
			return HttpResponse('submitted')

	form = AutomateFioForm()
	return render(request, 'fio_chart/automate_drive_benchmark_form.html', {'form': form})


# can try to convert this to pycurl later. currently creating subproc with curl cmd
def set_autopxe(lan_mac, cburn_img, burnin_dir):
	command = "%s RC=%s DIR=%s" %(cburn_img, RC_URL, burnin_dir)
	subprocess.Popen(['curl', '-X', 'POST', '-F', 'command=%s'%(command), '-F', 'address=%s'%(lan_mac), '-F', 'action=Update', \
					'172.16.0.3/cgi-bin/autopxe.php'])

# dont want to do reset because when system is initial off state, will not turn on
def reset_server(bmc_ip, bmc_username, bmc_password):
	subprocess.Popen(['ipmitool', '-U', bmc_username, '-P', bmc_password, '-H', bmc_ip, 'power', 'off'])
	time.sleep(10)
	subprocess.Popen(['ipmitool', '-U', bmc_username, '-P', bmc_password, '-H', bmc_ip, 'power', 'on'])

