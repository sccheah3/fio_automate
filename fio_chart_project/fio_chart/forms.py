from django import forms

class UploadFioLogForm(forms.Form):
    file = forms.FileField()

class AutomateFioForm(forms.Form):
	bmc_ip = forms.CharField()
	bmc_username = forms.CharField()
	bmc_password = forms.CharField()
	lan_mac = forms.CharField()
	cburn_img = forms.CharField()
	burnin_dir = forms.CharField()

class SavePerformanceForm(forms.Form):
	drive_info_file = forms.FileField()
	fio_log_file = forms.FileField()